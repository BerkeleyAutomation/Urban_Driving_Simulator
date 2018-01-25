from gym_urbandriving.assets.primitives import Polygon
import numpy as np

class Street(Polygon):
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
    points : 
       If specified, constructs this shape as a polygon
    """
    def __init__(self, x, y, xdim, ydim, angle=0, points=[]):
        if not points:
            self.angle = angle
            a = -self.angle
            corner_offsets = np.array([xdim / 2.0, ydim / 2.0])
            centers = np.array([x, y])
            signs = np.array([[1,1], [1,-1], [-1,-1], [-1,1]])
            corner_offsets = signs * corner_offsets
            rotation_mat = np.array([[np.cos(a), -np.sin(a)],
                                     [np.sin(a), np.cos(a)]])
            points = np.dot(corner_offsets, rotation_mat.T) + centers
        Polygon.__init__(self, points, self.angle, color=(30, 30, 30))

