import time
from search import search

test_queries  = [
    "python list",                                
    "how do I sort a dictionary by value",        
    "reverse a linked list",                      
    "segmentation fault in c",                    
    "java null pointer exception",               
    "how to center a div in css",                
    "postgresql composite primary key",         
    "memoization dynamic programming",      
    "convert string to datetime",         
    "why is my recursive function so slow", 
]

timings = []
for q in test_queries:
    start = time.perf_counter()
    results = search(q)
    elapsed = (time.perf_counter() - start) * 1000   # → milliseconds
    timings.append(elapsed)
    print(f"{elapsed:8.1f} ms   {q}")

print(f"\naverage: {sum(timings)/len(timings):.1f} ms")
print(f"fastest: {min(timings):.1f} ms")
print(f"slowest: {max(timings):.1f} ms")