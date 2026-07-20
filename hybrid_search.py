from search import search
from semantic_search import semantic_search
from rerank import rerank, blended_rerank
# k=60 (the standard default): controls how steeply top ranks dominate.
# small k -> rank 1 is king; large k -> ranks flatten. tunable, A/B later.
def hybrid_search(query, limit = 10, k = 60):
    keyword_results = search(query, limit = 50)
    semantic_results = semantic_search(query, limit = 50)

    scores = {} # accumulated RRF scores
    titles = {}

    # BM25 points and cosine distances are different units - they can't be
    # compared or added. But positions can: "my 3rd-best result" means the
    # same thing from any engine. So RRF keeps only positions:
    # place r in a list earns 1/(r + k) points.
    for rank, (qid, title, _) in enumerate(keyword_results):
        scores[qid] = scores.get(qid, 0) + 1 / (rank + 1 + k)
        titles[qid] = title

    # This second loop is where the two engines actually combine.
    # If a document already got points from the keyword loop above,
    # .get() finds them and this loop ADDS the semantic points on top.
    # So: seen by both engines = two contributions; seen by one = one.
    # That's why agreement wins - a doc at place 5 in BOTH lists
    # (1/65 + 1/65 = 0.031) beats a doc at place 1 in only ONE (1/61 = 0.016).
    for rank, (qid, title, _) in enumerate(semantic_results):
        scores[qid] = scores.get(qid, 0) + 1 / (rank + 1 + k)
        titles[qid] = title


    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [(qid, titles[qid], s) for qid, s in ranked[:limit]]

def full_search_ce_only(query, limit=10):
    fused = hybrid_search(query, limit=20)   # stage 1: retrieve wide
    return rerank(query, fused)[:limit]  # stage 2: judge narrow

def  full_search(query, limit=10):
    # variant of full_search: instead of letting the cross-encoder decide
    # alone, its ordering is RRF-fused with stage 1's ordering - the
    # consensus hedges the CE's phrase-echo weakness (see rerank.py)

    fused = hybrid_search(query, limit=20)
    return blended_rerank(query, fused)[:limit]

if __name__ == '__main__':
    for q in ["my loop never stops", "java null pointer exception"]:
        print("=" * 50)
        print("QUERY:", q)
        print("  --- fused (stage 1) ---")
        for qid, title, s in hybrid_search(q):
            print(f"  {s:.4f}  {title}")
        print("  --- reranked (stage 2) ---")
        for qid, title, s in full_search(q):
            print(f"  {s:.4f}  {title}")