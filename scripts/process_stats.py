import pstats
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))

p = pstats.Stats(os.path.join(dir_path, 'stats'))
p.strip_dirs().sort_stats("time").print_stats(15)
p.strip_dirs().sort_stats("time").print_callers(10)
