import numpy as np
from gym_urbandriving.assets.primitives import *

class Sidewalk(Rectangle):
    def __init__(self, x, y, xdim, ydim):
        Rectangle.__init__(self, x, y, xdim, ydim, sprite="gray.png");

