import csv
import psycopg2

conn = psycopg2.connect(dbname="stackoverflow", user="ajperiakzoltoeva")
cur = conn.cursor()

cur.execute("SELECT id FROM questions")
valid_question_ids = set(row[0] for row in cur.fetchall())
print(f"Loaded {len(valid_question_ids)} valid question IDs.")

insert_query = """
    INSERT INTO question_tags (question_id, tag)
    VALUES (%s, %s)
"""

inserted = 0
skipped = 0
with open('Tags.csv', encoding='ISO-8859-1') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            question_id = int(row['Id'])
        except ValueError:
            skipped += 1
            continue
        if question_id not in valid_question_ids:
            skipped += 1
            continue
        cur.execute(insert_query, (
            question_id,
            row['Tag'],
        ))
        inserted += 1
        
conn.commit()
print("Inserted")

cur.close()
conn.close()