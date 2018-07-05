import sys


def fluids_print(s, **kwargs):
    print("[FLUIDS] " + str(s), **kwargs)
def fluids_assert(cond, em):
    if not cond:
        fluids_print("Error: " + em)
        exit(1)
