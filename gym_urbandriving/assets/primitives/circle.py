import numpy as np
from gym_urbandriving.assets.primitives.shape import Shape


class Circle(Shape):
    def __init__(self, x, y, radius, angle=0.0, sprite="no_texture.png"):
        """
        Initializes rectangle object.

        Args:
            x: float, starting x position.
            y: float, starting y position.
            angle: float, starting angle of car in degrees.
        """
        Shape.__init__(self, x, y, sprite)
        self.angle = angle
        self.radius = radius
        self.primitive = Circle
