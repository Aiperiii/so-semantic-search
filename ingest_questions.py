import csv
import psycopg2
from datetime import datetime
conn = psycopg2.connect (dbname = "stackoverflow",
                         user = "ajperiakzoltoeva")
cur = conn.cursor()

def clean_date(value):
    if value == '':
        return None
    try:
        datetime.fromisoformat(value)
        return value
    except ValueError:
        return None

def clean_id(value):
    if value == '':
        return None
    try:
        return int(value)
    except ValueError:
        return None

insert_query = """
    INSERT INTO questions (id, title, body, score, owner_user_id, creation_date, closed_date)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

count = 0
with open("Questions.csv", encoding='ISO-8859-1') as file:
    reader = csv.DictReader(file)
    for row in reader:
        cur.execute(insert_query, (
            int(row["Id"]),
            row["Title"],
            row["Body"],
            int(row["Score"]) if row["Score"] else None,
            clean_id(row["OwnerUserId"]),
            clean_date(row['CreationDate']),
            clean_date(row['ClosedDate'])
        ))
        count += 1
        if count == 500000:
            break

conn.commit()

print("Inserted")

cur.close()
conn.close()