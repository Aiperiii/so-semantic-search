import time
import statistics
from concurrent.futures import ThreadPoolExecutor
import requests

URL = "http://127.0.0.1:8000/hybrid"

# a mix of queries so we're not just hitting one cached result
QUERIES = [
    "reverse a linked list", "python sort dictionary", "segmentation fault",
    "how to center a div", "sql join tables", "what is recursion",
    "javascript remove array element", "binary search tree", "null pointer",
    "read file line by line",
]

def one_request(i):
    q = QUERIES[i % len(QUERIES)]
    start = time.perf_counter()
    requests.get(URL, params={"q": q, "limit": 10})
    return (time.perf_counter() - start) * 1000   # ms

N = 100
print(f"firing {N} concurrent requests...")

overall_start = time.perf_counter()
with ThreadPoolExecutor(max_workers=20) as pool:
    timings = list(pool.map(one_request, range(N)))
overall = time.perf_counter() - overall_start

timings.sort()
p50 = statistics.median(timings)
p95 = timings[int(0.95 * N)]
p99 = timings[int(0.99 * N)]

print(f"\ncompleted {N} requests in {overall:.1f}s ({N/overall:.0f} req/sec)")
print(f"p50: {p50:.1f} ms")
print(f"p95: {p95:.1f} ms")
print(f"p99: {p99:.1f} ms")
print(f"min: {timings[0]:.1f} ms   max: {timings[-1]:.1f} ms") 
