import pygame
import numpy as np

from fluids.assets.shape import Shape
from fluids.assets.waypoint import Waypoint

class Lane(Shape):
    def __init__(self, start_wp=None, end_wp=None, **kwargs):
        #FCF59B
        Shape.__init__(self, color=(0xff, 0xff, 0xff), **kwargs)

        if start_wp is not None and end_wp is not None:
            self.start_waypoint = start_wp
            self.end_waypoint   = end_wp
        else:
            self.start_waypoint = (self.points[2] + self.points[3]) / 2
            self.end_waypoint   = (self.points[0] + self.points[1]) / 2

            self.start_waypoint = Waypoint(self.start_waypoint[0],
                                           self.start_waypoint[1],
                                           self,
                                           angle=self.angle)
            self.end_waypoint   = Waypoint(self.end_waypoint[0],
                                           self.end_waypoint[1],
                                           self,
                                           angle=self.angle)

            self.start_waypoint.nxt = [self.end_waypoint]
