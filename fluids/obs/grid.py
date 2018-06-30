from six import iteritems
import numpy as np
import pygame

from fluids.assets.shape import Shape

from fluids.obs.obs import FluidsObs
from fluids.utils import rotation_array

class GridObservation(FluidsObs):
    def __init__(self, car, grid_dim=500, grid_size=59):
        state = car.state
        self.car = car
        self.grid_dim = grid_dim
        self.grid_size = grid_size
        self.grid_square = Shape(x=car.x+grid_dim/3*np.cos(car.angle),
                                 y=car.y-grid_dim/3*np.sin(car.angle),
                                 xdim=grid_dim, ydim=grid_dim, angle=car.angle,
                                 color=None)
        self.all_collideables = []

        for k, obj in iteritems(state.objects):
            if car.can_collide(obj) and self.grid_square.intersects(obj):
                self.all_collideables.append(obj)

        self.small_square_size = self.grid_dim / self.grid_size
        x = self.grid_square.x
        y = self.grid_square.y
        angle = self.grid_square.angle
        points = []
        r_array = rotation_array(angle)
        self.colls = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.waypoints = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.raw_colls = {}
        for i in range(-int(self.grid_size/2), int(self.grid_size/2)+1):
            for j in range(-int(self.grid_size/2), int(self.grid_size/2)+1):
                point = np.array([i*self.small_square_size, j*self.small_square_size])
                p = point.dot(r_array)
                sx = p[0] + x
                sy = p[1] + y
        
                for obj in self.all_collideables:
                    if obj.contains_point((sx, sy)):
                        self.colls[i+int(self.grid_size/2)][j+int(self.grid_size/2)] = obj
                        self.raw_colls[(sx, sy)] = obj, None
                        break
                else:
                    self.raw_colls[(sx, sy)] = None, None
        

    def render(self, surface):
        from fluids.assets import Car, Lane, Sidewalk, Terrain
        
        self.grid_square.render(surface)
        if self.car.vis_level > 3:

            if self.car.vis_level > 4:
                for obj in self.all_collideables:
                    obj.render_debug(surface)

            for c, (obj, wp) in iteritems(self.raw_colls):
                color = obj.color if obj else (0, 255, 0)
                pygame.draw.circle(surface,
                                   color,
                                   (int(c[0]), int(c[1])),
                                   10)
                pygame.draw.circle(surface,
                                   (0, 0, 0),
                                   (int(c[0]), int(c[1])),
                                   10,
                                   5)
            debug_window = pygame.Surface((self.grid_dim, self.grid_dim))
            gd = self.grid_dim
            a0 = self.car.angle + np.pi/2
            a1 = self.car.angle
            for obj in self.all_collideables:
                rel_obj = obj.get_relative((self.car.x+gd/2*np.cos(a0)-gd/6*np.cos(a1),
                                            self.car.y-gd/2*np.sin(a0)+gd/6*np.sin(a1),
                                            self.car.angle))
                #rel_obj.render(debug_window)
            for i in range(len(self.colls)):
                for j in range(len(self.colls[0])):
                    obj = self.colls[i][j]
                    ic = (i) * self.small_square_size
                    jc = (j) * self.small_square_size
                    
                    color = obj.color if obj else (0, 255, 0)
                    pygame.draw.rect(debug_window, color,
                                     pygame.Rect((ic, jc),
                                                 (self.small_square_size, self.small_square_size)))


            surface.blit(debug_window, (surface.get_size()[0] - self.grid_dim, 0))        
            pygame.draw.rect(surface, (0, 0, 0),
                             pygame.Rect((surface.get_size()[0] - self.grid_dim-5, 0-5),
                                         (self.grid_dim+10, self.grid_dim+10)), 10)
            
