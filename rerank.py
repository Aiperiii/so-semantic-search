from sentence_transformers import CrossEncoder

reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def rerank(query, candidates):
    """candidates: list of (qid, title, rrf_score) from hybrid_search.
    Returns same shape re-ordered by cross-encoder relevance, with the
    cross-encoder's score replacing the RRF score."""

    pairs = [(query, title) for qid, title, _ in candidates]
    ce_scores = reranker.predict(pairs)          # one batched call - one score per pair
    reranked = sorted(zip(candidates, ce_scores), key=lambda x: x[1], reverse=True)
    
    return [(qid, title, float(s)) for (qid, title, _), s in reranked]

def blended_rerank(query, candidates, k=20):
    # candidates arrive already in stage-1 (RRF) order - that IS ordering #1.
    # get the cross-encoder's ordering - that's ordering #2:
    ce_ordered = rerank(query, candidates)

    # fuse the two orderings with the same RRF trick as hybrid_search:
    # each ordering gives each doc 1/(rank + k); agreement wins.
    scores = {}
    titles = {}
    for rank, (qid, title, _) in enumerate(candidates):      # stage-1 order
        scores[qid] = scores.get(qid, 0) + 1 / (rank + 1 + k)
        titles[qid] = title
    for rank, (qid, title, _) in enumerate(ce_ordered):      # CE order
        scores[qid] = scores.get(qid, 0) + 1 / (rank + 1 + k)

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [(qid, titles[qid], s) for qid, s in ranked]

