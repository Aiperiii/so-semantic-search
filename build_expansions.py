import psycopg2
import time

conn = psycopg2.connect(dbname = "stackoverflow", user = "ajperiakzoltoeva")
cur = conn.cursor()

start = time.perf_counter()

cur.execute("DROP TABLE IF EXISTS expansions;")

# for every token, its top-5 related tokens by lift * log(count).
# the pair table stores each pair once (alphabetical), so UNION ALL
# looks at it from both sides: a's partners and b's partners.
expansions_query = """
    CREATE TABLE expansions AS
    SELECT token, related, rank FROM (
        SELECT token, related, score,
            ROW_NUMBER() OVER (PARTITION BY token ORDER BY score DESC) AS rank
        FROM (
            SELECT c.token_a AS token, c.token_b AS related,
                c.count / (ta.df::numeric * tb.df / 500000) * LN(c.count) AS score
            FROM cooccurrence c
            JOIN token_stats ta ON ta.token = c.token_a
            JOIN token_stats tb ON tb.token = c.token_b
            WHERE c.count >= 5
            UNION ALL
            SELECT c.token_b AS token, c.token_a AS related,
                c.count / (ta.df::numeric * tb.df / 500000) * LN(c.count) AS score
            FROM cooccurrence c
            JOIN token_stats ta ON ta.token = c.token_a
            JOIN token_stats tb ON tb.token = c.token_b
            WHERE c.count >= 5
        ) both_directions
    ) ranked
    WHERE rank <= 5;
"""
cur.execute(expansions_query)
cur.execute("ALTER TABLE expansions ADD PRIMARY KEY (token, rank);")
conn.commit()

cur.execute("SELECT COUNT(*) FROM expansions")
print(f"built {cur.fetchone()[0]} expansion rows in {time.perf_counter() - start:.1f}s")

cur.close()
conn.close()

