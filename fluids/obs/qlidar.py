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
    beam_distribution: list of int
        If specified, uses a custom beam distribution. Values in this array are between [-1, 1].
        Ex: [-1, -0.5, 0, 0.5] corresponds to beams at -180, -90, 0, and 90 degree positions.
    """
    def __init__(self, car, det_range=200, n_beams=8, beam_distribution=[-1, -0.5, 0, 0.5]):
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

        if beam_distribution:
            n_beams     = len(beam_distribution)
            beam_deltas = np.array(beam_distribution) * np.pi
        else:
            beam_deltas = np.linspace(-1, 1, n_beams + 1) * np.pi
        self.linestrings = []
        self.detections = []
        for beam_delta in beam_deltas:
            beam_angle = car.angle + beam_delta

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
            self.detections.append([min_coll_d])

    def get_array(self):
        return np.array(self.detections)
            
    def render(self, surface):
        self.grid_square.render(surface, border=10)
        if self.car.vis_level > 4:
            for obj in self.all_collideables:
                obj.render_debug(surface)
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
                pygame.draw.line(surface,
                                 color,
                                 (self.car.x, self.car.y),
                                 (self.car.x+xd, self.car.y-yd),
                                 4)
                                 
