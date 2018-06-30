import pygame
import numpy as np

from fluids.assets.shape import Shape
from fluids.utils import Waypoint

class Lane(Shape):
    def __init__(self, **kwargs):
        Shape.__init__(self, color=(50, 50, 50), **kwargs)

        self.start_waypoint = (self.points[2] + self.points[3]) / 2
        self.end_waypoint   = (self.points[0] + self.points[1]) / 2

        self.start_waypoint = Waypoint(self.start_waypoint[0], self.start_waypoint[1], self.angle)
        self.end_waypoint   = Waypoint(self.end_waypoint[0], self.end_waypoint[1], self.angle)

        self.start_waypoint.nxt = [self.end_waypoint]
