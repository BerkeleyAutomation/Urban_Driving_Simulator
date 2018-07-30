from six import iteritems
import numpy as np
import pygame

from fluids.assets.shape import Shape
from fluids.obs.obs import FluidsObs
from fluids.utils import rotation_array

class GridObservation(FluidsObs):
    """
    Grid observation type. 
    Observation is an occupancy grid over the detection region. 
    Observation has 6 dimensions: terrain, drivable regions, illegal drivable regions, cars, pedestrians, and traffic lights.
    Array representation is (grid_size, grid_size, 6)
    """
    def __init__(self, car, obs_dim=500):
        from fluids.assets import ALL_OBJS, TrafficLight, Lane, Terrain, Sidewalk, \
            PedCrossing, Street, Car, Waypoint, Pedestrian
        state = car.state
        self.car = car
        self.grid_dim = obs_dim
        self.grid_square = Shape(x=car.x+obs_dim/3*np.cos(car.angle),
                                 y=car.y-obs_dim/3*np.sin(car.angle),
                                 xdim=obs_dim, ydim=obs_dim, angle=car.angle,
                                 color=None, border_color=(200,0,0))
        self.all_collideables = []
        collideable_map = {typ:[] for typ in ALL_OBJS}
        for k, obj in iteritems(state.objects):
            if (car.can_collide(obj) or type(obj) in {TrafficLight, Lane, Street}) and self.grid_square.intersects(obj):
                typ = type(obj)
                if typ not in collideable_map:
                    collideable_map[typ] = []
                collideable_map[typ].append(obj)
                self.all_collideables.append(obj)
        for waypoint in car.waypoints:
            collideable_map[Waypoint].append(waypoint)
            self.all_collideables.append(waypoint)

        terrain_window    = pygame.Surface((self.grid_dim, self.grid_dim))
        drivable_window   = pygame.Surface((self.grid_dim, self.grid_dim))
        undrivable_window = pygame.Surface((self.grid_dim, self.grid_dim))
        car_window        = pygame.Surface((self.grid_dim, self.grid_dim))
        ped_window        = pygame.Surface((self.grid_dim, self.grid_dim))
        light_window      = pygame.Surface((self.grid_dim, self.grid_dim))
        direction_window  = pygame.Surface((self.grid_dim, self.grid_dim))
        direction_pixel_window \
                          = pygame.Surface((self.grid_dim, self.grid_dim))
        direction_edge_window \
                          = pygame.Surface((self.grid_dim, self.grid_dim))

        gd = self.grid_dim
        a0 = self.car.angle + np.pi / 2
        a1 = self.car.angle
        rel = (self.car.x+gd/2*np.cos(a0)-gd/6*np.cos(a1),
               self.car.y-gd/2*np.sin(a0)+gd/6*np.sin(a1),
               self.car.angle)

        for typ in [Terrain, Sidewalk, PedCrossing]:
            for obj in collideable_map[typ]:
                rel_obj = obj.get_relative(rel)
                rel_obj.render(terrain_window, border=None)

        for obj in collideable_map[Lane]:
            rel_obj = obj.get_relative(rel)
            if not car.can_collide(obj):
                rel_obj.render(drivable_window, border=None)
            else:
                rel_obj.render(undrivable_window, border=None)
        for obj in collideable_map[Street]:
            rel_obj = obj.get_relative(rel)
            rel_obj.render(drivable_window, border=None)

        for obj in collideable_map[Car]:
            rel_obj = obj.get_relative(rel)
            rel_obj.render(car_window, border=None)

        for obj in collideable_map[Pedestrian]:
            rel_obj = obj.get_relative(rel)
            rel_obj.render(ped_window, border=None)
        for obj in collideable_map[TrafficLight]:
            rel_obj = obj.get_relative(rel)
            rel_obj.render(light_window, border=None)

        point = (int(gd/6), int(gd/2))
        edge_point = None

        def is_on_screen(point, gd):
            return 0 <= point[0] < gd and 0 <= point[1] < gd

        for p in self.car.waypoints:
            relp = p.get_relative(rel)
            new_point = int(relp.x), int(relp.y)
            if not edge_point and is_on_screen(point, gd) and not is_on_screen(new_point, gd):
                edge_point = new_point

            pygame.draw.line(direction_window, (255, 255, 255), point, new_point, 10)
            point = new_point

        edge_point = (min(gd - 1, max(0, edge_point[0])), min(gd - 1, max(0, edge_point[1])))

        pygame.draw.circle(direction_pixel_window, (255, 255, 255), edge_point, 10)

        if edge_point[0] == 0:
            pygame.draw.line(direction_edge_window, (255, 255, 255), (0, 0), (0, gd - 1), 10)
        if edge_point[0] == gd - 1:
            pygame.draw.line(direction_edge_window, (255, 255, 255), (gd - 1, 0), (gd - 1, gd - 1), 10)
        if edge_point[1] == 0:
            pygame.draw.line(direction_edge_window, (255, 255, 255), (0, 0), (gd - 1, 0), 10)
        if edge_point[1] == gd - 1:
            pygame.draw.line(direction_edge_window, (255, 255, 255), (0, gd - 1), (gd - 1, gd - 1), 10)


        self.pygame_rep = [pygame.transform.rotate(window, 90) for window in [terrain_window,
                                                                              drivable_window,
                                                                              undrivable_window,
                                                                              car_window,
                                                                              ped_window,
                                                                              light_window,
                                                                              direction_window,
                                                                              direction_pixel_window,
                                                                              direction_edge_window
                                                                              ]]

    def render(self, surface):
        self.grid_square.render(surface, border=10)
        if self.car.vis_level > 3:

            if self.car.vis_level > 4:
                for obj in self.all_collideables:
                    obj.render_debug(surface)
            for y in range(4):
                for x in range(2):
                    i = y + x * 4
                    if i < len(self.pygame_rep):
                        surface.blit(self.pygame_rep[i], (surface.get_size()[0] - self.grid_dim * (x+1), self.grid_dim * y))
                        pygame.draw.rect(surface, (200, 0, 0),
                                         pygame.Rect((surface.get_size()[0] - self.grid_dim*(x+1)-5, 0-5+self.grid_dim*y),
                                                     (self.grid_dim+10, self.grid_dim+10)), 10)

    def get_array(self):
        arr = np.zeros((self.grid_dim, self.grid_dim, len(self.pygame_rep)))
        for i in range(len(self.pygame_rep)):
            arr[:,:,i] = pygame.surfarray.array2d(self.pygame_rep[i]) > 0
        return arr
