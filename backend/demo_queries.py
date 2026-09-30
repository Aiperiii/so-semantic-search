# The semantic demo: six queries where keyword search fails for vocabulary
# reasons, collected across three weeks of evaluations. Run to show the
# three-layer story: BM25 fails -> expansion partially bridges -> semantic answers.


# results (first full-corpus run):
#   "difference between list and tuple" -> the ACTUAL comparison question at #1
#     (unreachable through three eval passes)
#   "my loop never stops" -> top 10 saturated with infinite-loop phrasings;
#     expansion's hard-won #1 result appears here effortlessly at #6
#   "flip the order of nodes" -> reversal questions, 7 of 10
#   "keep information after program closes" -> the whole persistence
#     vocabulary (save/persist/store) bridged
#   "when should I use recursion" -> a full board of explanatory content
#   "program crashes when input is empty" -> best board this query ever
#     produced (#1 is a near-paraphrase), then generic - semantic's honest
#     limit on generic-meaning queries

from sentence_transformers import SentenceTransformer
import psycopg2
from pgvector.psycopg2 import register_vector

model = SentenceTransformer('all-MiniLM-L6-v2')
conn = psycopg2.connect(dbname="stackoverflow", user="ajperiakzoltoeva")
register_vector(conn)
cur = conn.cursor()

DEMO_QUERIES = [
    "my loop never stops",
    "keep information after program closes",
    "flip the order of nodes in a linked list",
    "difference between list and tuple",
    "program crashes when input is empty",
    "when should I use recursion",
]

for q in DEMO_QUERIES:
    q_emb = model.encode(q)
    cur.execute("""SELECT title, embedding <=> %s AS dist
                   FROM questions ORDER BY dist LIMIT 10""", (q_emb,))
    print("=" * 60)
    print("QUERY:", q)
    for title, dist in cur.fetchall():
        print(f"  {dist:.4f}  {title}")