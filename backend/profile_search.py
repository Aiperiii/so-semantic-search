import cProfile, pstats
from search import search

cProfile.run('search("python list")', 'prof.out')
stats = pstats.Stats('prof.out')
stats.sort_stats('cumulative').print_stats(15)