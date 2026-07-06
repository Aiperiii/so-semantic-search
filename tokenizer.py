import re
from nltk.corpus import stopwords 
from nltk.stem import PorterStemmer

STOP_WORDS = set(stopwords.words('english'))
stemmer = PorterStemmer()


def tokenize(text):

    text = text.lower()

    # remove punctuation — keep only letters, digits, and spaces
    text = re.sub('[^a-z0-9\s]', ' ', text)

    tokens = text.split()
    
    # remove stopwords
    tokens  = [tk for tk in tokens if tk not in STOP_WORDS]

    # stem remaining tokens 
    tokens = [stemmer.stem(tk) for tk in tokens]

    return tokens

if __name__ == '__main__':
    print(tokenize("How to reverse a Linked List in Python?"))
    print(tokenize("Why doesn't Python's list.append() work here?"))
    print(tokenize("Python 3.9 throws TypeError code 500"))
    print(tokenize("What is this?"))