from gym_urbandriving.assets.primitives import *

class Street(Rectangle):
    def __init__(self, x, y, xdim, ydim):
        Rectangle.__init__(self, x, y, xdim, ydim, sprite="black.png");

