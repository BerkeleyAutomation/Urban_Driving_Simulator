import pygame

from fluids.assets.shape import Shape

class Street(Shape):
    def __init__(self, **kwargs):
        Shape.__init__(self, color=(0xff, 0xff, 0xff), **kwargs)
        self.in_waypoints = []
        self.out_waypoints = []
        self.intersection_waypoints = []
