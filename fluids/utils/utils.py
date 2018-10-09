import numpy as np
import os

def rotation_array(angle):
    cosa = np.cos(angle)
    sina = np.sin(angle)
    return np.array([[cosa, -sina],
                     [sina, cosa]])


def lookup_cache(fname):
    cache_folder = os.path.expanduser("~/.fluidscache/")
    if not os.path.exists(cache_folder):
        os.mkdir(cache_folder)
    fname = os.path.join(cache_folder, fname)
    if not os.path.exists(fname):
        return False
    return open(fname, "r")

def get_cache_filename(fname):
    cache_folder = os.path.expanduser("~/.fluidscache/")
    if not os.path.exists(cache_folder):
        os.mkdir(cache_folder)
    fname = os.path.join(cache_folder, fname)
    return fname

def distance(p0, p1):
    return np.linalg.norm([p0[0] - p1[0], p0[1] - p1[1]])
