# three-way comparison: stage-1 fusion vs CE-alone vs blended rerank.
# built to test the blend against the echo-problem queries + one control.
from hybrid_search import hybrid_search, full_search_ce_only, full_search

for q in ["my loop never stops", "program crashes when input is empty",
          "speed up sluggish script", "list index out of range"]:
    print("=" * 60)
    print("QUERY:", q)
    for name, fn in [("stage 1 (fused)", hybrid_search),
                     ("CE alone", full_search_ce_only),
                     ("blended", full_search)]:
        print(f"  --- {name} ---")
        for qid, title, s in fn(q, limit=5):
            print(f"  {s:.4f}  {title}")