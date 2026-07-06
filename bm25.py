from math import log

def bm25_score(tf, df, N, dl, avgdl, k1 = 1.5, b = 0.75):
    idf = log ((N - df + 0.5) / (df + 0.5) + 1)
    tf_norm = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / avgdl))
    return idf * tf_norm


if __name__ == '__main__':
    # D1: 'list' x4, dl=4
    print("D1:", bm25_score(tf=4, df=3, N=5, dl=4, avgdl=4))
    # D2: 'python' + 'list', tf=1 each, dl=2
    print("D2:", bm25_score(tf=1, df=2, N=5, dl=2, avgdl=4)
              + bm25_score(tf=1, df=3, N=5, dl=2, avgdl=4))
