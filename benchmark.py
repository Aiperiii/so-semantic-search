# Benchmark for search.py. 
# Run it twice: first run hits disk (cold),
# second run hits PostgreSQL's memory cache (warm).
#
# Week 2 baseline (frequency-sum ranking):
#   cold: avg 96.8 ms, worst 345.8 ms (python list)
#   warm: avg 12.1 ms, worst 25.8 ms
#   index build took 57.9 s
#
# Week 3 (BM25):
#   first run: avg 49.6 ms, worst 121.7 ms
#     (not truly cold - I had been searching a lot before running it)
#   warm: avg 28.0 ms, worst 83.8 ms
#   About 2x slower than week 2 - the bm25_score() call for every
#   candidate row is the main cost. Still under the 50 ms target.
#   Odd: "python list" was the slowest warm query (83.8) - probably
#   noise, check next time.
#
 
#   Week 4 (query expansion, expand=True is now the default):
#   First attempt - expansion computed per query with the big
#   cooccurrence JOIN. warm: avg 136.5 ms, EVERY query paid ~100ms
#   (even the tiny ones - fastest was 106.5!). That flat cost was
#   the giveaway: the expansion SQL ran the lift ranking over 1.9M
#   pairs on every search, recomputing answers that never change.

#   Fix: build_expansions.py precomputes top-5 for every token once
#   (25,365 rows, 0.3s)
#   
#   After fix:
#   first run: avg 74.7 ms, worst 253.3 ms 
#   warm: avg 34.1 ms, worst 65.4 ms
#   So expansion itself costs ~6 ms over BM25 (28.0 -> 34.1) - the
#   extra index lookups for expanded tokens. Under 50 ms target again.
#   "python list" back to normal (39.8) - week 3's 83.8 was noise.

# Week 5 (classifier + language boost + vote blending + no expansion for debug):
#
#   First benchmark came back BAD: avg ~97 ms, "python list" over 220 ms.
#   But none of the new features could explain it - they are all cheap.
#
#   How I found the real cause, step by step:
#   1. Put timers around each stage of search() - all the time was in
#      the scoring loop.
#   2. Ran cProfile - 86% of the time was in 34 SQL calls (~7 ms each).
#      The 20,000 bm25_score() calls cost only 9 ms total, so the math
#      was never the problem - the database calls were.
#   3. Ran EXPLAIN ANALYZE on one lookup - found it: the 9,628 rows for
#      "python" were spread across 7,133 different disk pages, because
#      the table was built question-by-question but is searched
#      token-by-token. PostgreSQL had to touch ~1 page per row.
#
#   The fix - one command:
#      CLUSTER inverted_index USING inverted_index_pkey;
#   This rewrites the table on disk in token order, so each token's rows
#   sit together. Pages touched for "python": 7,133 -> 53.
#   One lookup: 28 ms -> 6 ms.
#
#   After the fix:
#   warm: avg 25.3-26.5 ms, worst 49 ms ("why is my recursive function
#   so slow"). Fastest numbers of the whole project - with every week-5
#   feature turned on. "python list" now 18 ms, its best ever.
#
#   Note: CLUSTER is one-time. If the index is ever rebuilt, run it again
#   (reminder added in inverted_index.py).


# Week 6 (semantic embeddings):
#   embedded all 500k titles in 4.9 min (~1700/sec - Apple Silicon GPU via
#   MPS; roadmap budgeted a whole night for CPU).
#   first semantic search: 1.5-1.9 SECONDS per query - a linear scan
#   computing cosine distance against all 500k vectors. 

#   Fix: HNSW index (approximate nearest neighbor - trades ~1% recall for
#   ~25x speed; first deliberately-inexact component in the system).
#   Build note: default maintenance_work_mem (64MB) too small - postgres
#   warned mid-build; SET maintenance_work_mem = '2GB' first, then minutes.
#   After: 69-117 ms per semantic query. Keyword side unchanged at ~25 ms.

# Week 7 (hybrid fusion + cross-encoder re-ranking):
#   RRF fuses keyword + semantic ranked lists (50 deep each) - scores
#   discarded, only positions count, agreement wins.
#   Cross-encoder alone as re-ranker had a measured flaw: it inflates
#   titles that ECHO the query's wording over titles that answer it
#   (4 of 20 eval boards, distress-phrased queries). Fix: blend - the
#   CE's ordering is RRF-fused with stage 1's ordering, so consensus
#   hedges the judge. Echo residual now bounded to ~3 boards,
#   ordering-level only.
#   Full pipeline timing: ~136-191 ms steady state, ~160 typical.
#   First query of a fresh process pays ~500-1100 ms one-time model
#   warm-up (candidate fix: warm-up call at server start).
#   Budget was 200 ms: passing steady-state, tail grazes. Week 9 leads:
#   run the two engines concurrently (-25-40ms), cache, tame the tail.
#   Also: c-family tokenizer trigger formally retired this week -
#   semantic + CE handle c++ natively through the full funnel.

import time
from search import search
from hybrid_search import full_search

test_queries  = [
    "python list",                                
    "how do I sort a dictionary by value",        
    "reverse a linked list",                      
    "segmentation fault in c",                    
    "java null pointer exception",               
    "how to center a div in css",                
    "postgresql composite primary key",         
    "memoization dynamic programming",      
    "convert string to datetime",         
    "why is my recursive function so slow", 
]

timings = []
for q in test_queries:
    start = time.perf_counter()
    results = search(q)
    elapsed = (time.perf_counter() - start) * 1000   # → milliseconds
    timings.append(elapsed)
    print(f"{elapsed:8.1f} ms   {q}")

print(f"\naverage: {sum(timings)/len(timings):.1f} ms")
print(f"fastest: {min(timings):.1f} ms")
print(f"slowest: {max(timings):.1f} ms")

print()
print("--- full pipeline (hybrid + blended rerank) ---")
from hybrid_search import full_search

pipeline_timings = []
for q in test_queries:
    start = time.perf_counter()
    full_search(q)
    elapsed = (time.perf_counter() - start) * 1000
    pipeline_timings.append(elapsed)
    print(f"{elapsed:8.1f} ms   {q}")

print(f"\naverage: {sum(pipeline_timings)/len(pipeline_timings):.1f} ms")
print(f"fastest: {min(pipeline_timings):.1f} ms")
print(f"slowest: {max(pipeline_timings):.1f} ms")