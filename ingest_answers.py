import csv
import psycopg2
from datetime import datetime

def clean_id(value):
    if value == '':
        return None
    try:
        return int(value)
    except ValueError:
        return None

def clean_date(value):
    if value == '':
        return None
    try:
        datetime.fromisoformat(value)
        return value
    except ValueError:
        return None

conn = psycopg2.connect(dbname="stackoverflow", user="ajperiakzoltoeva")
cur = conn.cursor()

cur.execute("SELECT id FROM questions")
valid_question_ids = set(row[0] for row in cur.fetchall())
print(f"Loaded {len(valid_question_ids)} valid question IDs.")

insert_query = """
    INSERT INTO answers (id, question_id, body, score, owner_user_id, creation_date)
    VALUES (%s, %s, %s, %s, %s, %s)
"""

inserted = 0
skipped = 0
with open('Answers.csv', encoding='ISO-8859-1') as f:
    reader = csv.DictReader(f)
    for row in reader:
        parent_id = clean_id(row['ParentId'])
        if parent_id not in valid_question_ids:
            skipped += 1
            continue
        cur.execute(insert_query, (
            int(row['Id']),
            parent_id,
            row['Body'],
            int(row['Score']) if row['Score'] else None,
            clean_id(row['OwnerUserId']),
            clean_date(row['CreationDate']),
        ))
        inserted += 1
        
conn.commit()

print("Inserted")

cur.close()
conn.close()