import psycopg2

conn = psycopg2.connect(dbname = "stackoverflow", user = "ajperiakzoltoeva")
cur = conn.cursor()


# ranking rule: lift * log(count)
# lift = observed cooccurrences / expected by chance (df_a * df_b / N)
#   -> filters out popularity (common words collapse to lift ~1)
# log(count) = evidence with diminishing returns

expansion_sql = """
    SELECT CASE WHEN c.token_a = %s THEN c.token_b ELSE c.token_a END AS other,
           c.count / (ta.df::numeric * tb.df / 500000) * LN(c.count) AS score
    FROM cooccurrence c
    JOIN token_stats ta ON ta.token = c.token_a
    JOIN token_stats tb ON tb.token = c.token_b
    WHERE (c.token_a = %s OR c.token_b = %s)
      AND c.count >= 5
    ORDER BY score DESC
    LIMIT %s
"""


def expand_token(token, top_n = 5):
    """
    return the top_n related tokens for a given token by lift * log(count)
    """
    cur.execute(expansion_sql, (token,token, token, top_n))
    return [row[0] for row in cur.fetchall()]



if __name__ == '__main__':
    for tk in ['loop', 'sort', 'python', 'error', 'list']:
        print(tk, ':', expand_token(tk))
