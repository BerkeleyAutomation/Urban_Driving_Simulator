import numpy as np
from gym_urbandriving.assets.primitives.shape import Shape
from copy import deepcopy
import shapely.geometry

class Polygon(Shape):
    def __init__(self, points, angle=0, color=(255, 255, 255)):
        """
        Initializes Polygon object.

        Args:
            points: list, vertices of polygon
            angle: float, Angle of polygon. 
            color: RGB color of polygon
        """
        xs, ys = zip(*points)
        Shape.__init__(self, sum(xs)/len(xs), sum(ys)/len(ys), angle, 0, static=True)
        self.primitive = Polygon
        self.points = points
        self.minx = min([p[0] for p in points])
        self.maxx = max([p[0] for p in points])
        self.miny = min([p[1] for p in points])
        self.maxy = max([p[1] for p in points])
        self.color = color

    def get_shapely_obj(self):
        if self.shapely_obj:
            return self.shapely_obj
        self.shapely_obj = shapely.geometry.Polygon(self.points)
        return self.shapely_obj
