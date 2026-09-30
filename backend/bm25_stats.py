import psycopg2

conn = psycopg2.connect(dbname = "stackoverflow", user = "ajperiakzoltoeva")
cur = conn.cursor()

# create doc_stats table containing length of each doc
cur.execute("DROP TABLE IF EXISTS doc_stats;")

query1 = """
    CREATE TABLE doc_stats AS
    SELECT question_id, SUM(frequency) AS dl
    FROM inverted_index
    GROUP BY question_id;
"""
cur.execute(query1)
cur.execute("ALTER TABLE doc_stats ADD PRIMARY KEY (question_id);")


# create token_stats table containing document frequency of each token
cur.execute("DROP TABLE IF EXISTS token_stats;")

query2 = """
    CREATE TABLE token_stats AS
    SELECT token, COUNT(*) AS df
    FROM inverted_index
    GROUP BY token;
"""

cur.execute(query2)
cur.execute("ALTER TABLE token_stats ADD PRIMARY KEY (token);")


conn.commit()

cur.close()
conn.close()

