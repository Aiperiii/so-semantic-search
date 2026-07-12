from fastapi import FastAPI, Query
from search import search 
app = FastAPI()

@app.get("/search")
def search_query(q : str, limit : int  = Query(default=10, ge=1, le=100), expand: bool = True):

    results = search(q, limit, expand)
    return [{"question_id" : question_id, "title" : title, "score" : score} 
            for question_id, title, score in results]

