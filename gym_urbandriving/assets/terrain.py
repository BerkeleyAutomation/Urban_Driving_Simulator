import numpy as np
from gym_urbandriving.assets.primitives.rectangle import Rectangle

class Terrain(Rectangle):
    """
    Represents a square of impassable terrain
    
    Parameters
    ----------
    x : float
       Upper left x coordinate of the terrain block
    y : float
       Upper left y coordinate of the terrain block
    xdim : float
       Width of the terrain block
    ydim : float
       Height of the terrain block
    """
    def __init__(self, x, y, xdim, ydim):
        sprite = ["block1.png", "block2.png", "block3.png", "block4.png"][np.random.randint(0, 3)]
        Rectangle.__init__(self, x, y, xdim, ydim, sprite="grass.jpg", static=True);

