# rerun with expansion : ~5 queries better, 2-3 worse, rest unchanged.
# pattern: expansion helps when tokens have specific ecosystems (loop,
# recursion, join), hurts when tokens are generic (read, line, input) or
# when the real problem was never vocabulary (language routing, conceptual
# intent, tokenizer bugs). biggest regression: "read file line by line
# python" - expansion amplified the wrong-language problem

from search import search

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
    "segmentation fault when accessing array",
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
    print("  --- without expansion ---")
    for question_id, title, score in search(q, limit=5, expand=False):
        print(f"  {score:6.2f}  {title}")
    print("  --- with expansion ---")
    for question_id, title, score in search(q, limit=5, expand=True):
        print(f"  {score:6.2f}  {title}")