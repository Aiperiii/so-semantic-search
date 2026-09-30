import psycopg2

conn = psycopg2.connect(
    dbname="stackoverflow",
    user="ajperiakzoltoeva"
)
print("Connected succeesfully")
conn.close()