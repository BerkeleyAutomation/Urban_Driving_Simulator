from six import iteritems
import numpy as np
import pygame

from fluids.assets.shape import Shape

from fluids.obs.obs import FluidsObs
from fluids.utils import rotation_array

class BirdsEyeObservation(FluidsObs):
    def __init__(self, car, obs_dim=500):
        from fluids.assets import Car, Lane, Sidewalk, Terrain, TrafficLight, Waypoint, PedCrossing
        state = car.state
        self.car = car
        self.grid_dim = obs_dim
        self.grid_square = Shape(x=car.x+obs_dim/3*np.cos(car.angle),
                                 y=car.y-obs_dim/3*np.sin(car.angle),
                                 xdim=obs_dim, ydim=obs_dim, angle=car.angle,
                                 color=None)
        self.all_collideables = []
        collideable_map = {Waypoint:[]}
        for k, obj in iteritems(state.objects):
            if car.can_collide(obj) and self.grid_square.intersects(obj):
                typ = type(obj)
                if typ not in collideable_map:
                    collideable_map[typ] = []
                collideable_map[typ].append(obj)
                self.all_collideables.append(obj)
        for waypoint in car.waypoints:
            collideable_map[Waypoint].append(waypoint)
            self.all_collideables.append(waypoint)

        debug_window = pygame.Surface((self.grid_dim, self.grid_dim))
        gd = self.grid_dim
        a0 = self.car.angle + np.pi / 2
        a1 = self.car.angle
        for typ in [Terrain, Sidewalk, Lane, Car, TrafficLight, Waypoint, PedCrossing]:
            if typ in collideable_map:
                for obj in collideable_map[typ]:
                    rel_obj = obj.get_relative((self.car.x+gd/2*np.cos(a0)-gd/6*np.cos(a1),
                                                self.car.y-gd/2*np.sin(a0)+gd/6*np.sin(a1),
                                                self.car.angle))
                    rel_obj.render(debug_window, border=None)
        self.pygame_rep = pygame.transform.rotate(debug_window, 90)


    def render(self, surface):


        self.grid_square.render(surface)
        if self.car.vis_level > 3:

            if self.car.vis_level > 4:
                for obj in self.all_collideables:
                    obj.render_debug(surface)

            surface.blit(self.pygame_rep, (surface.get_size()[0] - self.grid_dim, 0))        
            pygame.draw.rect(surface, (0, 0, 0),
                             pygame.Rect((surface.get_size()[0] - self.grid_dim-5, 0-5),
                                         (self.grid_dim+10, self.grid_dim+10)), 10)

    def get_array(self):
        arr = pygame.surfarray.array3d(self.pygame_rep)
        return arr
