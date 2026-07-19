from sentence_transformers import SentenceTransformer
import psycopg2
from pgvector.psycopg2 import register_vector

model = SentenceTransformer('all-MiniLM-L6-v2')
conn = psycopg2.connect(dbname = "stackoverflow", user = "ajperiakzoltoeva")
register_vector(conn)
cur = conn.cursor()

def semantic_search(query, limit = 10):

    """ORDER BY dist uses the HNSW index (approximate nearest neighbor) -
    without it this was a 1.9s linear scan over all 500k vectors; ~70ms with.
    returns (question_id, title, distance)"""

    q_emb = model.encode(query)

    cur.execute("""SELECT id, title, embedding <=> %s AS dist
                   FROM questions
                   ORDER BY dist
                   LIMIT %s""", (q_emb, limit))

    return cur.fetchall()


if __name__ == '__main__':
    for q in ["my loop never stops",                          
              "how to create multidimasional array in c++?"]: # typo + c++
        print("=" * 50)
        print("QUERY:", q)
        for qid, title, dist in semantic_search(q):
            print(f"  {dist:.4f}  {title}")
