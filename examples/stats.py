"""
Example of reading cProfile stats

Usage:
  python examples/stats.py temp/stats
"""

import pstats
p = pstats.Stats('temp/stats')
p.strip_dirs().sort_stats(2).print_stats(20)
