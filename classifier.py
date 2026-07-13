DEBUG_SIGNALS = ['error', 'except', 'fail', 'crash', 
                'wrong', 'stuck', 'hang', 'not working', 
                'traceback', 'segfault']

LANGUAGES = ['python', 'javascript', 'java', 'c', 'c++', 
            'c#', 'objective-c', 'ruby', 'php', 'sql', 
            'html', 'css', 'jquery']

IMPLEMENT_VERBS = ['implement', 'create', 'write', 'design', 'build']

QUESTION_WORDS = ['how', 'why', 'when', 'where', 'what', 'difference','vs']


def classify_query(query):
    query = query.lower()
    terms = query.split()
    terms = [t.strip('?.,!:;()"\'') for t in terms]

    if any(sig in query for sig in DEBUG_SIGNALS):      # substring, whole string
        return "debug"
    if any(w in terms for w in LANGUAGES + IMPLEMENT_VERBS):   # whole-word
        return "code"
    if any(w in terms for w in QUESTION_WORDS):          # whole-word
        return "conceptual"
    return "general"

    
if __name__ == '__main__':
    tests = [
        "my c++ segment tree gives wrong answer",   # expect debug
        "read file line by line python",            # expect code
        "what is a pointer",                        # expect conceptual
        "merge two sorted arrays",                  # expect code
        "what is c++?",                             # expect code 
        "string methods in c++?",
        "can't find why my code fails" ,
        "git merge conflict error"                  # expect code
    ]
    for q in tests:
        print(f"{classify_query(q):12}  {q}")

