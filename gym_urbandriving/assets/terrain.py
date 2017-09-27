import numpy as np
from gym_urbandriving.assets.primitives.rectangle import Rectangle

class Terrain(Rectangle):
    def __init__(self, x, y, xdim, ydim):
        sprite = ["block1.png", "block2.png", "block3.png", "block4.png"][np.random.randint(0, 3)]
        Rectangle.__init__(self, x, y, xdim, ydim, sprite=sprite);

