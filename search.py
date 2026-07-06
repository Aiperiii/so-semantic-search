import psycopg2
from tokenizer import tokenize

conn = psycopg2.connect(dbname = "stackoverflow", user = "ajperiakzoltoeva")
cur = conn.cursor()

def search(query, limit = 10):
    # same tokenizer as the index builder
    tokens = tokenize(query)

    # accumulative per question score : a question matching several
    # query tokens gets the sum of tokens' frequencies 
    scores = {}

    for tk in tokens:
        cur.execute("SELECT question_id,frequency FROM inverted_index WHERE token = %s ", (tk, ))
        rows = cur.fetchall()
        
        for question_id, frequency in rows:
            scores[question_id] = scores.get(question_id, 0) + frequency
    
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