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
        ("my c++ segment tree gives wrong answer", "debug"),
        ("read file line by line python", "code"),
        ("what is a pointer", "conceptual"),
        ("merge two sorted arrays", "general"),
        ("what is c++?", "code"),
        ("string methods in c++?", "code"),
        ("can't find why my code fails", "debug"),
        ("git merge conflict error", "debug"),
    ]
    correct = 0
    for q, expected in tests:
        actual = classify_query(q)
        status = "✓" if actual == expected else "✗"
        if actual == expected:
            correct += 1
        print(f"{status}  {actual:12}  expected: {expected:12}  {q}")
    print(f"\nAccuracy: {correct}/{len(tests)} = {correct/len(tests)*100:.0f}%")

