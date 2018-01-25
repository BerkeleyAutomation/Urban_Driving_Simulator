import numpy as np
from gym_urbandriving.assets.primitives.shape import Shape
from copy import deepcopy
import shapely.geometry

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
        self.orthogonal = self.static and not self.angle % (np.pi/2)
        if self.orthogonal:
            self.min_x = min([t[0] for t in self.corners])
            self.max_x = max([t[0] for t in self.corners])
            self.min_y = min([t[1] for t in self.corners])
            self.max_y = max([t[1] for t in self.corners])

    def get_shapely_obj(self):
        if self.shapely_obj:
            return self.shapely_obj
        self.shapely_obj = shapely.geometry.Polygon(self.get_corners())
        return self.shapely_obj
    
    def get_corners(self):
        if self._x == self.x and self._y == self.y and self._angle == self.angle:
            return self.corners
        self._x = self.x
        self._y = self.y
        self._angle = self.angle
        
        angle = -self.angle
        corner_offsets = np.array([self.xdim / 2.0, self.ydim / 2.0])
        centers = np.array([self.x, self.y])
        signs = np.array([[1,1], [1,-1], [-1,-1], [-1,1]])
        corner_offsets = signs * corner_offsets
        rotation_mat = np.array([[np.cos(angle), -np.sin(angle)],
                                 [np.sin(angle), np.cos(angle)]])
        rotated_corners = np.dot(corner_offsets, rotation_mat.T) + centers
        self.corners = rotated_corners
        return rotated_corners
