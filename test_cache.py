import time, requests

url = "http://127.0.0.1:8000/hybrid?q=reverse a linked list&limit=10"

# first call - likely a cache miss (full pipeline)
t = time.perf_counter()
requests.get(url)
print(f"first call (miss): {(time.perf_counter()-t)*1000:.1f} ms")

# second call - cache hit
t = time.perf_counter()
requests.get(url)
print(f"second call (hit): {(time.perf_counter()-t)*1000:.1f} ms")