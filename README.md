# Stack Overflow Semantic Search

A search engine over 500,000 Stack Overflow questions that understands meaning, not just keywords. Combines BM25 keyword ranking with semantic vector embeddings, fused via Reciprocal Rank Fusion, plus a cross-encoder re-ranking stage for precision.

**Live demo:** _(link coming after deploy)_ · **Demo video:** _(YouTube link coming)_

---

## Why I built it

I wanted to understand how real search actually works — not the tutorial version that wraps a single library call, but the production version: how keyword and semantic retrieval are combined, why re-ranking exists, and how you make it fast enough to feel instant. So I built the whole pipeline from the ground up, reasoning through every design decision, rather than gluing APIs together.

---

## What it does

Type a natural-language question and get the ten most relevant Stack Overflow questions, matched by meaning. A toggle switches between **keyword-only** and the **full hybrid + AI-reranked** pipeline, so you can see exactly what the semantic layers add.

| Query | Keyword-only finds | Hybrid finds |
|---|---|---|
| "my loop never stops" | *"BackgroundWorkers never stop being busy"*, *"Java process never stops"* — word matches, wrong meaning | *"Loop keeps going after being carried out"* — one shared word, right meaning |
| "keep information after program closes" | *"Audio keeps playing after force close"*, *"Android app keeps Force Closing"* — matches "close", misses the intent | *"How to persist / save program information"*, *"Application that saves progress after closing"* — understands you want to save data |

---

## Architecture

```
                          user query
                              │
              ┌───────────────┴───────────────┐
              ▼                                ▼
      KEYWORD ENGINE                    SEMANTIC ENGINE
   BM25 + query expansion            embed query (MiniLM)
   + intent classifier               → HNSW search over
   (top 50)                            pgvector (top 50)
              │                                │
              └───────────────┬────────────────┘
                              ▼
                   RECIPROCAL RANK FUSION
                 (vote by rank, not by score)
                              │
                              ▼  top 20
                       CROSS-ENCODER
              (reads query + title together)
                              │
                              ▼
                     BLEND → top 10 results
```

- **PostgreSQL + pgvector** stores 500k questions and their 384-dim embeddings; an **HNSW index** turns a 1.9 s linear scan into a ~70 ms nearest-neighbour lookup.
- **Redis** caches identical queries for one hour (~2.5 ms on a repeat).
- **FastAPI** backend, **React + Vite** frontend.

---

## Benchmark numbers

| Metric | Result |
|---|---|
| Keyword search (warm) | ~25 ms |
| Full hybrid pipeline (steady state) | ~160 ms |
| Cached repeat query | ~2.5 ms (**~240× faster**) |
| Semantic search: linear scan → HNSW | 1.9 s → ~70 ms |
| Embedding all 500k titles | 4.9 min (Apple Silicon GPU) |
| 100 concurrent requests (4 workers) | **p50 18 ms · p95 80 ms · p99 1.25 s** |

With a single worker, concurrent requests serialized and p95 hit 17 s; four uvicorn workers brought it to 80 ms — a ~200× tail improvement, found by load-testing and fixed by re-measuring.

---

## Tech stack

**Backend:** Python, FastAPI, PostgreSQL + pgvector, Redis
**Search / ML:** sentence-transformers (MiniLM bi-encoder + cross-encoder), NLTK, custom BM25
**Frontend:** React, Vite, plain CSS
**Infra:** Railway (backend, DB, cache), Vercel (frontend)

---

## Running locally

```bash
# PostgreSQL with the pgvector extension, database "stackoverflow"
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
redis-server &
uvicorn main:app --workers 4      # API on :8000

cd frontend && npm install && npm run dev   # UI on :5173
```

---

## What I'd build next

- **Observability:** Prometheus + Grafana (queries/sec, latency percentiles, cache-hit rate).
- **Connection pooling** so a single worker can handle real concurrency (the load test showed it serializes on one shared DB connection).
- **Corpus coverage:** the data is a 2008–2016 sample, so some queries find nothing simply because the answer post-dates it — a current dump would fix this.
- **Learned re-ranking** to replace the rule-based intent classifier, plus a distance cutoff so nonsense queries return "no strong matches" instead of nearest-but-irrelevant results.
