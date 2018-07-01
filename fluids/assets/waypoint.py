import numpy as np
import pygame
import shapely.geometry

import scipy.interpolate as si
from fluids.assets.shape import Shape

def plan(x0,y0,a0,x1,y1,a1):
    def interpolate(p0,p1,p2,p3,t):
        return [p0[0]*1.0*((1-t)**3) + p1[0]*3.0*t*(1-t)**2 + p2[0]*3.0*(t**2)*(1-t) + p3[0]*1.0*(t**3),
                p0[1]*1.0*((1-t)**3) + p1[1]*3.0*t*(1-t)**2 + p2[1]*3.0*(t**2)*(1-t) + p3[1]*1.0*(t**3)]

    distance_between_points = np.sqrt((x0-x1)**2+(y0-y1)**2)
    p0 = [x0,y0]
    p1 = [x0+.3*distance_between_points*np.cos(a0), y0 - .3*distance_between_points*np.sin(a0)]
    p2 = [x1-.3*distance_between_points*np.cos(a1), y1 + .3*distance_between_points*np.sin(a1)]
    p3 = [x1,y1]

    first_point = interpolate(p0,p1,p2,p3,0)
    res_path = [first_point]
    for t in np.arange(0,1,.001):
        new_point = interpolate(p0,p1,p2,p3,t)
        old_point = res_path[-1]
        if (new_point[0] - old_point[0])**2 + (new_point[1] - old_point[1])**2 > 3000:
            res_path.append(new_point)
    res_path.append([x1, y1])
    return res_path

class Waypoint(Shape):
    def __init__(self, x, y, angle=0, nxt=None):

        self.radius = 0
        self.nxt   = nxt if nxt else []
        self.prv   = []
        points = [(x-1, y-1),
                  (x+1, y-1),
                  (x+1, y+1),
                  (x-1, y+1)]

        super(Waypoint, self).__init__(angle=angle, points=points, color=(0, 255, 255))

    def smoothen(self, max_dangle=np.pi/5):
        all_news = []
        new_nxt = []
        for n_p in self.nxt:

            path = plan(self.x, self.y, self.angle % (2 * np.pi),
                        n_p.x, n_p.y, n_p.angle % (2 * np.pi))
            new_point = Waypoint(path[1][0], path[1][1])
            all_news.append(new_point)
            new_nxt.append(new_point)
            for i in range(2, len(path) - 1):
                next_p = Waypoint(path[i][0], path[i][1])
                all_news.append(next_p)
                new_point.nxt = [next_p]
                new_point = next_p
            new_point.nxt = [n_p]
        self.nxt = new_nxt
        return all_news

    def render(self, surface, **kwargs):
        pygame.draw.circle(surface,
                           (0, 255, 255),
                           (int(self.x), int(self.y)),
                           5)
        if "nxt" in self.__dict__:
            for next_point in self.nxt:
                pygame.draw.line(surface,
                                 (0, 255, 255),
                                 (int(self.x), int(self.y)),
                                 (int(next_point.x), int(next_point.y)),
                                 1)
