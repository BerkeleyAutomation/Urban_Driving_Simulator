import sys


def print(s):
    sys.stdout.write("[FLUIDS] " + str(s) + '\n')
def fluids_assert(cond, em):
    if not cond:
        print("Error: " + em)
        exit(1)
