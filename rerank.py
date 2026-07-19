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
