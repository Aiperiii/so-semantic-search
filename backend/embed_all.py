# full run: 500k titles in 4.9 min at ~1700 titles/sec (Apple Silicon GPU via MPS)

# after a full re-embed from scratch, ensure the HNSW index exists:
#   SET maintenance_work_mem = '2GB';
#   CREATE INDEX ON questions USING hnsw (embedding vector_cosine_ops);
from sentence_transformers import SentenceTransformer, util
import psycopg2
from pgvector.psycopg2 import register_vector
import time

model = SentenceTransformer('all-MiniLM-L6-v2')

conn = psycopg2.connect(dbname = "stackoverflow", user = "ajperiakzoltoeva")
cur = conn.cursor()

register_vector(conn)

start = time.perf_counter()
done = 0
batch  = 1000

while True:
    cur.execute("SELECT id, title FROM questions WHERE embedding IS NULL LIMIT %s", (batch, ))
    rows = cur.fetchall()
    if not rows:
        break

    titles = [r[1] for r in rows]
    ids = [r[0] for r in rows]

    embeddings  = model.encode(titles)

    for qid, emb in zip(ids, embeddings):
        cur.execute("UPDATE questions SET embedding = %s WHERE id = %s", (emb, qid))
    conn.commit()

    done += len(rows)
    elapsed = time.perf_counter() - start
    print(f"{done} embedded, {elapsed/60:.1f} min, "
          f"{done/elapsed:.0f} titles/sec", flush=True)


cur.close()
conn.close()