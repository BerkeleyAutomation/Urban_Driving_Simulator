import pygame

from fluids.assets.shape import Shape

class Street(Shape):
    def __init__(self, **kwargs):
        Shape.__init__(self, color=(30, 30, 30), **kwargs)
        self.in_waypoints = []
        self.out_waypoints = []
