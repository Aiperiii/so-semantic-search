import psycopg2 
from tokenizer import tokenize
from collections import Counter
conn = psycopg2.connect(dbname = "stackoverflow", user = "ajperiakzoltoeva")
cur = conn.cursor()

# create inverted_index table
sql_query = """
    CREATE TABLE IF NOT EXISTS inverted_index( 
        token TEXT NOT NULL,
        question_id INTEGER NOT NULL,
        frequency INTEGER NOT NULL,
        PRIMARY KEY(token, question_id)
        );
    """
cur.execute(sql_query)
conn.commit()

cur.execute("SELECT id, title FROM questions")
rows = cur.fetchall()

for i, (question_id, title) in enumerate(rows):
    if title is None:
        continue
    # tokenize title
    tokens = tokenize(title)

    # count frequency of tokens in the title 
    counts = Counter(tokens)

    # inserts tokens into inverted_index
    for token, freq in counts.items():
        cur.execute("INSERT INTO inverted_index (token, question_id, frequency) VALUES(%s, %s, %s)",
                    (token, question_id, freq))

    # commit every 10000 questions
    if i % 10000 == 0:
        conn.commit()

# final commit for the tail      
conn.commit()

cur.close()
conn.close()
