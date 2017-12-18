import numpy as np
from gym_urbandriving.assets.primitives import Rectangle, Polygon
from gym_urbandriving.assets.pedestrian import Pedestrian

class Sidewalk(Polygon):
    """
    Represents a block of sidewalk. Passable for pedestrians, not for cars

    Parameters
    ----------
    x : float
       Upper left x coordinate of the sidewalk block
    y : float
       Upper left y coordinate of the sidewalk block
    xdim : float
       Width of the sidewalk block
    ydim : float
       Height of the sidewalk block
    points : list
       If specified, constructs sidewalk as polygon
    """
    def __init__(self, x, y, xdim, ydim, angle=0.0, points=[]):
        if not points:
            a = angle % 360
            a = np.radians(-a)
            corner_offsets = np.array([xdim / 2.0, ydim / 2.0])
            centers = np.array([x, y])
            signs = np.array([[1,1], [1,-1], [-1,-1], [-1,1]])
            corner_offsets = signs * corner_offsets
            rotation_mat = np.array([[np.cos(a), -np.sin(a)],
                                     [np.sin(a), np.cos(a)]])
            points = np.dot(corner_offsets, rotation_mat.T) + centers
        Polygon.__init__(self, points, angle, color=(150, 150, 150))


    def generate_man(self, man_type=Pedestrian):
        """
        Generates a man on the sidewalk

        Returns
        -------
        Pedestrian
            Generated Pedestrian object
        """

        x = np.random.uniform(self.minx,
                              self.maxx)
        y = np.random.uniform(self.miny,
                              self.maxy)
        man = man_type(x, y, angle=self.angle)
        return man
