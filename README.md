# Stack Overflow Semantic Search

A search engine over 500,000 Stack Overflow questions that understands meaning, not just keywords. Combines BM25 keyword ranking with semantic vector embeddings, fused via Reciprocal Rank Fusion, plus a cross-encoder re-ranking stage for precision.

*Built on the [Kaggle StackSample dataset](https://www.kaggle.com/datasets/stackoverflow/stacksample) — Stack Overflow questions from 2008–2013.*

 **Demo video:** [Watch on YouTube]_(https://youtu.be/EE3qJya5fs0)_

---

## Why I built it

I wanted to understand how real search actually works — not the tutorial version that wraps a single library call, but the production version: how keyword and semantic retrieval are combined, why re-ranking exists, and how you make it fast enough to feel instant. So I built the whole pipeline from the ground up, reasoning through every design decision, rather than gluing APIs together.

---

## What it does

Type a natural-language question and get the ten most relevant Stack Overflow questions, matched by meaning. A toggle switches between **keyword-only** and the **full hybrid + AI-reranked** pipeline, so you can see exactly what the semantic layers add.

| Query | Keyword-only finds | Hybrid finds |
|---|---|---|
| "difference between list and tuple" | *"LINQ: List of tuples to tuple of lists"*, *"Create a list (of tuples?) from two lists of different sizes"* — conversion questions, not the comparison | *"python: list vs tuple, when to use each?"* at #1 — the actual comparison |
| "my program is using too much memory" | *"Measure how much memory a program will need"* — matches the words, but about *measuring* memory | *"Program using up all my memory"* at #1 — understands the actual problem |

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
| Keyword search (warm) | ~5–65 ms |
| Full hybrid pipeline (steady state) | ~200–250 ms |
| Cached repeat query | ~5 ms (**~40× faster**) |
| Semantic search: linear scan → HNSW | 1.9 s → ~10–150 ms (re-verified) |
| Embedding all 500k titles | 4.9 min (Apple Silicon GPU) |
| 100 concurrent requests, 1 worker (cold cache) | p50 144 ms · p95 440 ms |
| 100 concurrent requests, 4 workers (cold cache) | **p50 51 ms · p95 235 ms** |

Running four uvicorn workers roughly halved latency under concurrent load by handling requests in parallel. With a warm cache — as real traffic has repeated queries — Redis pulls p95 well under 150 ms, since repeat queries return in ~2.5 ms. Throughput measured at ~80–90 requests/sec.

---

## Tech stack

**Backend:** Python, FastAPI, PostgreSQL + pgvector, Redis
**Search / ML:** sentence-transformers (MiniLM bi-encoder + cross-encoder), NLTK, custom BM25
**Frontend:** React, Vite, plain CSS

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
- **Corpus coverage:** the data is a 2008–2013 sample, so some queries find nothing simply because the answer post-dates it — a current dump would fix this.
- **Learned re-ranking** to replace the rule-based intent classifier, plus a distance cutoff so nonsense queries return "no strong matches" instead of nearest-but-irrelevant results.
