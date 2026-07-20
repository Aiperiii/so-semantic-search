# rerun with expansion : ~5 queries better, 2-3 worse, rest unchanged.
# pattern: expansion helps when tokens have specific ecosystems (loop,
# recursion, join), hurts when tokens are generic (read, line, input) or
# when the real problem was never vocabulary (language routing, conceptual
# intent, tokenizer bugs). biggest regression: "read file line by line
# python" - expansion amplified the wrong-language problem

# week 5 rerun: language boost tested at 2.5 (too strong - language beat
# topic) then 1.8 via A/B - kept 1.8. javascript-remove query still slightly
# off. vote blending surfaced "Pointer vs. Reference" (the corpus's
# top-voted pointer question) to #2 - the canonical "what is a pointer"
# question doesn't exist in this 10% sample.

from search import search
from hybrid_search import hybrid_search, full_search

queries = [
    # cat 1 — exact keyword (expect: good)
    "python sort list",
    "java null pointer exception",
    "read file line by line python",
    "javascript remove element from array",
    "sql join two tables",
    # cat 2 — paraphrase (expect: fail)
    "my loop never stops",
    "speed up sluggish script",
    "flip the order of nodes in a linked list",
    "program crashes when input is empty",
    "keep information after program closes",
    # cat 3 — error style (expect: mixed)
    "list index out of range",
    "cannot read property of undefined",
    "segmentation fault in c",
    # cat 4 — conceptual (expect: mixed/fail)
    "difference between list and tuple",
    "when should I use recursion",
    "why use interfaces",
    "what is a pointer",
    # cat 5 — tokenizer limitations (expect: fail, known why)
    "c++ vector vs array",
    "python 3.9 new features",
    "getElementById returns null",
]

for q in queries:
    print("=" * 60)
    print("QUERY: ", q)
    print("  --- fused (stage 1) ---")
    for qid, title, s in hybrid_search(q, limit=5):
        print(f"  {s:.4f}  {title}")
    print("  --- reranked (stage 2) ---")
    for qid, title, s in full_search(q, limit=5)[:5]:
        print(f"  {s:.4f}  {title}")