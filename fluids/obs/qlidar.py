from six import iteritems
import numpy as np
import pygame
import shapely

from fluids.obs.obs import FluidsObs
from fluids.utils import distance, fluids_assert

class QLidarObservation(FluidsObs):
    """
    QLidar observation type.

    Parameters
    ----------
    det_range: int
        Detection range of lidar beams
    n_beams: int
        Number of uniformly spaced beams to use, when using uniform beam distribution
    beam_distribution: list of float
        If specified, uses a custom beam distribution. Values in this array are between [-1, 1].
        Ex: [-1, -0.5, 0, 0.5] corresponds to beams at -180, -90, 0, and 90 degree positions.
    goal_distance: int
        The number of waypoint steps to look ahead when generating a "goal direction vector"
    """
    def __init__(self, car, det_range=200, n_beams=8, beam_distribution=None,
                 goal_distance=4):
        from fluids.assets import Shape

        state = car.state

        self.car = car
        self.det_range = det_range

        self.grid_square = Shape(x=car.x, y=car.y,
                                 xdim=det_range*2, ydim=det_range*2,
                                 angle=car.angle,
                                 color=None)

        self.all_collideables = []

        for c in self.car.collideables:
            for k, obj in iteritems(state.type_map[c]):
                if car.can_collide(obj) and self.grid_square.intersects(obj):
                    self.all_collideables.append(obj)


        x, y = car.x, car.y
        goal_distance = min(goal_distance, len(car.waypoints)-1)
        goal_wp = car.waypoints[goal_distance]
        goalx, goaly = goal_wp.x, goal_wp.y



        if (goalx == x):
            if y - goaly > 0:
                gangle = np.pi / 2
            else:
                gangle = -np.pi / 2
        else:
            gangle = (np.arctan((y - goaly) / (goalx - x)) % (2 * np.pi))
        if (goalx - x < 0):
            gangle = gangle + np.pi
        gangle = gangle % (2 * np.pi)
            #gangle = car.angle
        if np.any(beam_distribution):
            n_beams     = len(beam_distribution)
            beam_deltas = np.array(beam_distribution) * np.pi
        else:
            beam_deltas = np.linspace(-1, 1, n_beams + 1) * np.pi
        self.linestrings = []
        self.detections = []
        for beam_delta in beam_deltas:
            beam_angle = (car.angle + beam_delta) % (2 * np.pi)

            xd = x + np.cos(beam_angle) * det_range
            yd = y - np.sin(beam_angle) * det_range
            linestring = shapely.geometry.LineString([(x, y), (xd, yd)])
            self.linestrings.append((beam_delta, linestring))

            min_coll_d = det_range
            for obj in self.all_collideables:
                isect = linestring.intersection(obj.shapely_obj)
                if not isect.is_empty:
                    d = distance((x, y), list(isect.coords)[0])
                    if d < min_coll_d:
                        min_coll_d = d

            d_gangle = min(abs(beam_angle - gangle),
                           2*np.pi - abs(beam_angle - gangle))


            self.detections.append([min_coll_d, d_gangle])

        self.detections = np.array(self.detections)

        min_angle_index = min(enumerate(self.detections[:,1]), key=lambda x:x[1])[0]
        self.detections[:,1] = 0
        self.detections[min_angle_index,1] = 1

    def get_array(self):
        return np.array(self.detections)
            
    def render(self, surface):
        self.grid_square.render(surface, border=10)
        if self.car.vis_level > 4:
            # for obj in self.all_collideables:
            #     obj.render_debug(surface)
            # xd = np.cos(self.gangle) * 100
            # yd = np.sin(self.gangle) * 100
            # pygame.draw.circle(surface,
            #                    (0, 0, 255),
            #                    (int(self.car.x+xd), int(self.car.y-yd)),
            #                    10)
            # pygame.draw.circle(surface,
            #                    (0, 0, 255),
            #                    (int(self.goalx), int(self.goaly)),
            #                    10)

            for det, (beam_delta, ls) in \
                zip(self.detections, self.linestrings):

                # pygame.draw.line(surface, (0, 255, 0),
                #                  (self.car.x, self.car.y),
                #                  ls.coords[1],
                #                  5)
                angle = beam_delta + self.car.angle
                xd = np.cos(angle) * det[0]
                yd = np.sin(angle) * det[0]

                
                color = (255, 0, 0)
                if det[0] == self.det_range:
                    color = (0, 255, 0)

                if det[1]:
                    pygame.draw.circle(surface,
                                       (0, 0, 255),
                                       (int(self.car.x+xd), int(self.car.y-yd)),
                                       10)
                pygame.draw.line(surface,
                                 color,
                                 (self.car.x, self.car.y),
                                 (self.car.x+xd, self.car.y-yd),
                                 4)
                                 
