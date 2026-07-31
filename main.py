from fastapi import FastAPI, Query
from search import search 
from hybrid_search import full_search
from fastapi.middleware.cors import CORSMiddleware
import redis
import json

cache = redis.Redis(host='localhost', port=6379, decode_responses=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# the full pipeline: keyword + semantic, RRF-fused, cross-encoder re-ranked,
# blended with the fusion ordering. This is what the frontend uses.
# results cached in redis for 1h - identical repeat queries return instantly.
@app.get("/hybrid")
def hybrid_endpoint(q: str, limit: int = Query(default=10, ge=1, le=100)):
    key = f"hybrid:{q}:{limit}"

    cached = cache.get(key)
    if cached is not None:
        return json.loads(cached)

    results = full_search(q, limit)
    response = [
        {"question_id": qid, "title": title, "score": score}
        for qid, title, score in results
    ]
    cache.set(key, json.dumps(response), ex=3600)
    return response
    
# keyword-only search: BM25 + expansion + classifier boosts.
# kept as the baseline - useful for showing what the semantic layers add.
@app.get("/search")
def search_query(q : str, limit : int  = Query(default=10, ge=1, le=100), expand: bool = True):

    results = search(q, limit, expand)
    return [{"question_id" : question_id, "title" : title, "score" : score} 
            for question_id, title, score in results]

