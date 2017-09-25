import numpy as np
from gym_urbandriving.assets.primitives.shape import Shape


class Rectangle(Shape):
    def __init__(self, x, y, xdim, ydim, angle=0, sprite="no_texture.png"):
        """
        Initializes rectangle object.

        Args:
            x: float, starting x position.
            y: float, starting y position.
            angle: float, starting angle of car in degrees.
        """
        Shape.__init__(self, x, y, sprite)
        self.angle = angle
        self.xdim = xdim
        self.ydim = ydim
        self.halfdiag = np.linalg.norm([xdim, ydim]) / 2
        self._x, self._y = None, None
        self.corners = self.get_corners()
        self.primitive = Rectangle

    def get_corners(self):
        if self._x == self.x and self._y == self.y:
            return self.corners
        self._x = self.x
        self._y = self.y
        
        angle = np.radians(self.angle)
        corner_offsets = np.array([self.xdim / 2.0, self.ydim / 2.0])
        centers = np.array([self.x, self.y])
        signs = np.array([[1,1], [1,-1], [-1,1], [-1,-1]])
        corner_offsets = signs * corner_offsets
        rotation_mat = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        rotated_corners = np.dot(corner_offsets, rotation_mat.T) + centers
        self.corners = rotated_corners
        return rotated_corners
    
    def contains_point(self, point):
        a, b, c, d = self.get_corners()
        AM, AB, AC = point - a, b - a, c - a
        c1 = 0 <= np.dot(AM, AB) <= np.dot(AB, AB)
        c2 = 0 <= np.dot(AM, AC) <= np.dot(AC, AC)
        contains = c1 and c2
        return contains

