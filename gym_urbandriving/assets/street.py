from gym_urbandriving.assets.primitives.rectangle import Rectangle

class Street(Rectangle):
    """
    Represents a block of street. Passable for cars and pedestrians.
    Does not have directionality associated with it, so use this for
    the middle of an intersection

    Parameters
    ----------
    x : float
       Upper left x coordinate of the street block
    y : float
       Upper left y coordinate of the street block
    xdim : float
       Width of the street block
    ydim : float
       Height of the street block
    """
    def __init__(self, x, y, xdim, ydim):
        Rectangle.__init__(self, x, y, xdim, ydim, angle=0.0, sprite="black.png", static=True);

