import random
import numpy as np
import shapely
import pygame
from fluids.assets.shape import Shape

class Pedestrian(Shape):
    def __init__(self, max_vel=2, vel=0, planning_depth=2, **kwargs):
        Shape.__init__(self, color=(255, 150, 150), xdim=20, ydim=20, **kwargs)
        self.max_vel        = max_vel
        self.vel            = vel
        self.waypoints      = []
        self.trajectory     = []
        self.planning_depth = planning_depth

    def get_future_shape(self):
        if len(self.waypoints) and len(self.trajectory):
            line = shapely.geometry.LineString([(self.waypoints[0].x, self.waypoints[0].y),
                                                (self.x, self.y)]).buffer(self.ydim * 0.5, resolution=2)
            return shapely.geometry.MultiPolygon([t[2] for t in self.trajectory[:int(self.vel)]]
                                                 + [self.shapely_obj, line]).buffer(self.ydim*0.2, resolution=2)
        else:
            return self.shapely_obj.buffer(self.ydim*0.3, resolution=2)
    def step(self, action):
        if len(self.waypoints) and action:
            x0, y0 = self.x, self.y
            x1, y1 = self.waypoints[0].x, self.waypoints[0].y
            angle = np.arctan2([y0-y1], [x1-x0])[0]
            self.x = self.x + 1 * np.cos(angle)
            self.y = self.y - 1 * np.sin(angle)
            self.angle = angle
            self.update_points()
        while len(self.waypoints) < self.planning_depth and len(self.waypoints) and len(self.waypoints[-1].nxt):
            next_waypoint = random.choice(self.waypoints[-1].nxt)
            line = shapely.geometry.LineString([(self.waypoints[-1].x, self.waypoints[-1].y),
                                                (next_waypoint.x, next_waypoint.y)]).buffer(self.ydim*0.5)
            self.trajectory.append(((self.waypoints[-1].x, self.waypoints[-1].y),
                                    (next_waypoint.x, next_waypoint.y), line))
            self.waypoints.append(next_waypoint)
            
        if len(self.waypoints) and self.intersects(self.waypoints[0]):
            self.waypoints.pop(0)
            if len(self.trajectory):
                self.trajectory.pop(0)

    def can_collide(self, other):
        from fluids.assets import CrossWalkLight
        if type(other) is CrossWalkLight:
            if other.color == (200, 0, 0):
                return super(Pedestrian, self).can_collide(other)
            return False
        return super(Pedestrian, self.can_collide(other))

    def render(self, surface, **kwargs):
        super(Pedestrian, self).render(surface, **kwargs)
        if "waypoints" not in self.__dict__:
            return
        if len(self.waypoints) and self.vis_level > 1:
            pygame.draw.line(surface,
                             (255, 0, 0),
                             (self.x, self.y),
                             (self.waypoints[0].x, self.waypoints[0].y),
                             2)
            for line in self.trajectory:
                pygame.draw.line(surface,
                                 (255, 0, 0),
                                 line[0],
                                 line[1],
                                 2)
        if len(self.waypoints) and self.vis_level > 2:
            blob = self.get_future_shape()

            traj_ob = list(zip(*(blob).exterior.coords.xy))

            pygame.draw.polygon(surface,
                                (175, 175, 175),
                                traj_ob,
                                5)

