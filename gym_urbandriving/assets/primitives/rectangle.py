import numpy as np
from gym_urbandriving.assets.primitives.shape import Shape
from copy import deepcopy

class Rectangle(Shape):
    def __init__(self, x, y, xdim, ydim, angle=0, mass=1, sprite="no_texture.png",
                 static=False):
        """
        Initializes rectangle object.

        Args:
            x: float, starting x position.
            y: float, starting y position.
            angle: float, starting angle of car in degrees.
        """
        Shape.__init__(self, x, y, angle, mass, sprite=sprite, static=static)
        self.xdim = xdim
        self.ydim = ydim
        self.halfdiag = np.linalg.norm([xdim, ydim]) / 2
        self._x, self._y = None, None
        self.corners = self.get_corners()
        self.primitive = Rectangle
        self.orthogonal = self.static and not self.angle % 90
        if self.orthogonal:
            self.min_x = min([t[0] for t in self.corners])
            self.max_x = max([t[0] for t in self.corners])
            self.min_y = min([t[1] for t in self.corners])
            self.max_y = max([t[1] for t in self.corners])
    def get_corners(self):
        if self._x == self.x and self._y == self.y and self._angle == self.angle:
            return self.corners
        self._x = self.x
        self._y = self.y
        self._angle = self.angle
        
        angle = np.radians(-self.angle)
        corner_offsets = np.array([self.xdim / 2.0, self.ydim / 2.0])
        centers = np.array([self.x, self.y])
        signs = np.array([[1,1], [1,-1], [-1,1], [-1,-1]])
        corner_offsets = signs * corner_offsets
        rotation_mat = np.array([[np.cos(angle), -np.sin(angle)],
                                 [np.sin(angle), np.cos(angle)]])
        rotated_corners = np.dot(corner_offsets, rotation_mat.T) + centers
        self.corners = rotated_corners
        return rotated_corners
    
    def contains_point(self, point):
        # if self.orthogonal:
        #     x, y = point
        #     return self.min_x < x < self.max_x and self.min_y < y < self.max_y
        a, b, c, d = self.get_corners()
        AM, AB, AC = point - a, b - a, c - a
        c1 = 0 <= np.dot(AM, AB) <= np.dot(AB, AB)
        c2 = 0 <= np.dot(AM, AC) <= np.dot(AC, AC)
        contains = c1 and c2
        return contains

 
