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


import time
from search import search

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