import numpy as np
from copy import deepcopy
import shapely.geometry
import os
import IPython
import pygame
import numpy.linalg as LA

SPRITE_DIR = "gym_urbandriving/visualizer/sprites/"


class Shape(object):
    trajectory = None
    def __init__(self, x, y, angle, mass, sprite="no_texture.png", static=False):
        self.x = x
        self.y = y
        self.angle = angle % (2*np.pi)
        self.mass = mass
        basedir = os.path.dirname(__file__)
        filename = os.path.join(basedir, "../../visualizer/sprites/", sprite)
        self.sprite = pygame.image.load(filename)
        self.static = static
        self.pygame_sprite = None
        self.shapely_obj = None

    def get_pos(self):
        return (self.x,self.y)
        #return np.array([self.x, self.y])

    def intersect(self, other):
        return self.get_shapely_obj().intersects(other.get_shapely_obj())

    def contains_point(self, point):
        return self.get_shapely_obj().contains(shapely.geometry.Point(point))

    def contains_point_numpy(self,point):

        a = abs(self.x - point[0])
        b = abs(self.y - point[1])

        return max(a,b) < 40

    def dist_to(self, other):
        return self.get_shapely_obj().distance(other.get_shapely_obj())

    def get_sprite(self):
        return self.sprite

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k is "shapely_obj":
                setattr(result, k, None)
            elif k is "sprite":
                setattr(result, k, self.sprite)
            else:
                setattr(result, k, deepcopy(v, memo))
        return result

    def collides(self, other):
        return self.can_collide(other) and self.intersect(other)
