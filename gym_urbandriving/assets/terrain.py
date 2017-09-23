import numpy as np
from gym_urbandriving.assets.primitives import *

class Terrain(Rectangle):
    def __init__(self, x, y, xdim, ydim):
        Rectangle.__init__(self, x, y, xdim, ydim, sprite="brown.png");
