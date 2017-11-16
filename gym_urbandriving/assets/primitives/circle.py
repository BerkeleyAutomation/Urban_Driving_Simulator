import numpy as np
from gym_urbandriving.assets.primitives.shape import Shape
from copy import deepcopy
import shapely.geometry

class Circle(Shape):
    def __init__(self, x, y, radius, angle=0.0, mass=100, sprite="no_texture.png", static=False):
        """
        Initializes rectangle object.

        Args:
            x: float, starting x position.
            y: float, starting y position.
            angle: float, starting angle of car in degrees.
        """
        Shape.__init__(self, x, y, angle, mass, sprite=sprite, static=static)
        self.radius = radius
        self.primitive = Circle

    def get_shapely_obj(self):
        if self.shapely_obj:
            return self.shapely_obj
        self.shapely_obj = shapely.geometry.Point(self.get_pos()).buffer(self.radius)
        return self.shapely_obj
