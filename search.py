import psycopg2
from tokenizer import tokenize
from bm25 import bm25_score
from expansion import expand_token
from classifier import classify_query, LANGUAGES
from math import log


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

# scores of questions
cur.execute("SELECT id, score FROM questions")
VOTES = dict(cur.fetchall())


def search(query, limit = 10, expand = True):
    # label saved for later (debug/conceptual strategies).
    # language boost is on for all query types: naming a language = wanting it.
    label = classify_query(query)

    # languages(tokens) that are included in the query
    query_languages = [w for w in query.lower().split() 
                       if w.strip('?.,!:;()"\'') in LANGUAGES]

    tokens = tokenize(query)

    boost_tokens = set()
    for lang in query_languages:
        boost_tokens.update(tokenize(lang)) 

    LANG_BOOST = 1.8  # tunable, 2.5 was too strong (language beat topic). A/B test picked 1.8.
                      # still slightly off on one eval query - good enough for now.
    weighted = [(tk, LANG_BOOST if tk in boost_tokens else 1.0) for tk in tokens]

    if expand:
        for tk in tokens:
            for ex in expand_token(tk):
                if ex not in tokens:          
                    weighted.append((ex, 0.3))

    # accumulate per-question BM25 score: a question matching several
    # query tokens gets the sum of per-token BM25 scores
    scores = {}

    for tk, weight in weighted:

        cur.execute("SELECT df FROM token_stats WHERE token = %s", (tk, ))
        row = cur.fetchone()
        if row is None:
            continue
        df = row[0]

        cur.execute("SELECT question_id,frequency FROM inverted_index WHERE token = %s ", (tk, ))
        rows = cur.fetchall()
        
        for question_id, frequency in rows:
            dl = DL[question_id]
            scores[question_id] = scores.get(question_id, 0) + weight * bm25_score(frequency, df, N, dl, avgdl)
    
    
    VOTE_ALPHA = 0.8   # tunable, same status as 0.3 and 1.8
    if label == 'conceptual':
        for qid in scores:
            scores[qid] += VOTE_ALPHA * log(1 + max(VOTES[qid], 0))

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
    print("--- expand=False ---")
    for qid, title, score in search("my loop never stops", expand=False):
        print(f"{score:6.2f}  {title}")
    print("--- expand=True ---")
    for qid, title, score in search("my loop never stops", expand=True):
        print(f"{score:6.2f}  {title}")
    print("-----------")
    for qid, title, score in search("read file line by line python", limit=20, expand=False):
        print(f"{score:6.2f}  {title}")

    print("-----------")
    for qid, title, score in search("what is a pointer", limit=20, expand=False):
        print(f"{score:6.2f}  {title}")

