import psycopg2
import time
from tokenizer import tokenize
from itertools import combinations

conn = psycopg2.connect(dbname = "stackoverflow", user = "ajperiakzoltoeva")
cur = conn.cursor()

# create cooccurrence table
# count pairs across all titles in a dict 
sql_query = """
    CREATE TABLE IF NOT EXISTS cooccurrence( 
        token_a TEXT NOT NULL,
        token_b TEXT NOT NULL,
        count INTEGER NOT NULL,
        PRIMARY KEY(token_a, token_b)
        );
    """
cur.execute(sql_query)
conn.commit()

start = time.perf_counter()

# count pairs across all titles in a dict
cur.execute("SELECT id, title FROM questions")
pair_counts = {}

for (question_id, title) in cur.fetchall():
    
    if title is None:
        continue
    # alphabetical order so (a,b) and (b,a) are always the same row
    tokens = sorted(set(tokenize(title)))
    
    for a, b in combinations(tokens, 2):
        pair_counts[(a,b)] = pair_counts.get((a,b), 0) + 1
    

count_time = time.perf_counter() - start
print(f"counting done: {count_time:.1f}s, {len(pair_counts)} distinct pairs")


for i, ((a, b), cnt) in enumerate(pair_counts.items()):
    cur.execute(
        "INSERT INTO cooccurrence (token_a, token_b, count) VALUES (%s, %s, %s)",
        (a, b, cnt)
    )
    if i % 100000 == 0:
        conn.commit()

conn.commit()

total = time.perf_counter() - start
print(f"total: {total:.1f}s ({total - count_time:.1f}s writing)")

cur.close()
conn.close()
