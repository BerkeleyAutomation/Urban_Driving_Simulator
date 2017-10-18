import numpy as np
from gym_urbandriving.assets.primitives.shape import Shape
from copy import deepcopy

class Circle(Shape):
    def __init__(self, x, y, radius, angle=0.0, mass=100, sprite="no_texture.png"):
        """
        Initializes rectangle object.

        Args:
            x: float, starting x position.
            y: float, starting y position.
            angle: float, starting angle of car in degrees.
        """
        Shape.__init__(self, x, y, angle, mass, sprite)
        self.radius = radius
        self.primitive = Circle
        
    def contains_point(self, point):
        d = np.linalg.norm([self.x - point[0], self.y - point[1]])
        return d < self.radius
