import numpy as np
import pygame
import shapely.geometry

from fluids.utils import rotation_array

class Shape(object):
    def __init__(self, x=0, y=0,
                 xdim=0, ydim=0,
                 points=[],
                 mass=0,
                 type=None,
                 angle=0, angle_deg=0,
                 color=(255, 255, 255),
                 border_color=(0xE4, 0xE4, 0xE4),
                 vis_level=1,
                 state=None,
                 collideables=[],
                 waypoints=None):

        if angle_deg:
            angle = np.deg2rad(angle_deg)
        if not len(points):
            corner_offsets = np.array([xdim / 2.0, ydim / 2.0])
            centers = np.array([x, y])
            signs = np.array([[1,1], [1,-1], [-1,-1], [-1,1]])
            corner_offsets = signs * corner_offsets
            rotation_mat = rotation_array(angle)
            self.x, self.y = x, y
            self.origin_points = corner_offsets
        else:
            xs, ys = zip(*points)
            self.x, self.y = sum(xs) / len(xs), sum(ys) / len(ys)
            self.origin_points = points - np.array([self.x, self.y])

        self.points = self.origin_points.dot(rotation_array(angle)) + np.array([self.x,
                                                                                self.y])

        xs, ys = zip(*self.points)
        self.minx, self.maxx = min(xs), max(xs)
        self.miny, self.maxy = min(ys), max(ys)
        centers = np.array([self.x, self.y])
        self.radius = max(np.linalg.norm([p -  centers for p in self.points], axis=1))

        self.xdim          = xdim
        self.ydim          = ydim

        self.angle         = angle
        self.mass          = mass
        self.vis_level     = vis_level
        self.collideables  = collideables
        self.shapely_obj   = shapely.geometry.Polygon(self.points)
        self.color         = color
        self.border_color  = border_color
        self.state         = state
        self.waypoints     = [] if not waypoints else waypoints
    def intersects(self, other):
        return self.shapely_obj.intersects(other.shapely_obj)

    def get_relative(self, other, offset=(0,0)):
        if type(other) == tuple:
            x, y, angle = other
        else:
            x, y, angle = other.x, other.y, other.angle
        new_points = self.points - np.array([x, y])
        new_points = new_points.dot(rotation_array(-angle))
        new_points = new_points + np.array(offset)
        shape = Shape(points=new_points[:,:2], color=self.color)
        shape.__class__ = type(self)
        return shape

    def center_distance_to(self, other):
        return np.linalg.norm([self.x-other.x, self.y-other.y])

    def can_collide(self, other):
        return type(other) in self.collideables and self is not other
    def collides(self, other):
        return self.can_collide(other) and self.intersects(other)

    def contains_point(self, point, buf=0):
        if point[0] + buf < self.minx or point[0] - buf > self.maxx \
           or point[1] + buf < self.miny or point[1] - buf > self.maxy:
            return False
        if buf:
            return self.shapely_obj.buffer(buf).contains(shapely.geometry.Point(point))
        return self.shapely_obj.contains(shapely.geometry.Point(point))

    def dist_to(self, other):
        return self.shapely_obj.distance(other.shapely_obj)

    def render(self, surface, border=4, color=None):
        if not color:
            color = self.color
        if color:
            pygame.draw.polygon(surface, color, self.points)
        if border:
            pygame.draw.polygon(surface, self.border_color, self.points, border)

    def render_debug(self, surface, color=(255, 0, 0), width=10):
        pygame.draw.polygon(surface, color, self.points, width)

    def step(self, actions):
        pass

    def update_points(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        origin = np.array([self.x, self.y])
        self.points = self.origin_points.dot(rotation_array(self.angle)) + origin
        xs, ys = self.points[:,0], self.points[:,1]
        self.minx, self.maxx = min(xs), max(xs)
        self.miny, self.maxy = min(ys), max(ys)
        self.shapely_obj = shapely.geometry.Polygon(self.points)

        
