import psycopg2

conn = psycopg2.connect(dbname = "stackoverflow", user = "ajperiakzoltoeva")
cur = conn.cursor()

# load all expansions into a dict once at startup:
#   {token: [related1, related2, ...]}
# the table is precomputed by build_expansions.py - computing
# rankings during every search was costing ~100ms per query

cur.execute("SELECT token, related FROM expansions ORDER BY token, rank;")
EXPANSIONS = {}

for token,related in cur.fetchall():
    EXPANSIONS.setdefault(token, []).append(related)


def expand_token(token, top_n = 5):
    """
    return the top_n related tokens for a given token by lift * log(count)
    """
    return EXPANSIONS.get(token, [])[ : top_n]



if __name__ == '__main__':
    for tk in ['loop', 'sort', 'python', 'error', 'list']:
        print(tk, ':', expand_token(tk))
