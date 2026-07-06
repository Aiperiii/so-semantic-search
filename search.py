import psycopg2
from tokenizer import tokenize
from bm25 import bm25_score

conn = psycopg2.connect(dbname = "stackoverflow", user = "ajperiakzoltoeva")
cur = conn.cursor()

# total number of documents/questions
cur.execute("SELECT COUNT(*) FROM questions")
N = cur.fetchone()[0]

# avarage length of all documents/questions
cur.execute("SELECT AVG(dl) FROM doc_stats")
avgdl = float(cur.fetchone()[0])

# all documents' lengths saved in dict
cur.execute("SELECT question_id, dl FROM doc_stats")
DL = dict(cur.fetchall())


def search(query, limit = 10):
    # same tokenizer as the index builder
    tokens = tokenize(query)

    # accumulate per-question BM25 score: a question matching several
    # query tokens gets the sum of per-token BM25 scores
    scores = {}

    for tk in tokens:

        cur.execute("SELECT df FROM token_stats WHERE token = %s", (tk, ))
        row = cur.fetchone()
        if row is None:
            continue
        df = row[0]

        cur.execute("SELECT question_id,frequency FROM inverted_index WHERE token = %s ", (tk, ))
        rows = cur.fetchall()
        
        for question_id, frequency in rows:
            dl = DL[question_id]
            
            scores[question_id] = scores.get(question_id, 0) + bm25_score(frequency, df, N, dl, avgdl)
    
    # sorted in decreasing order of scores
    scores = sorted(scores.items(), key = lambda x : x[1], reverse = True)
    
    results = []
    
    # min() guards against queries with fewer matches than limit
    for i in range(min(limit, len(scores))):
        question_id = scores[i][0]

        cur.execute("SELECT title FROM questions WHERE id = %s", (question_id, ))
        title = cur.fetchone()[0]

        results.append((question_id, title, scores[i][1]))

    return results


if __name__ == '__main__':
    for question_id, title, score in search("python list"):
        print(score, question_id, title)
