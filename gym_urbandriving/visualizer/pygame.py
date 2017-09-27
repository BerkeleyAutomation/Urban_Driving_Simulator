from gym_urbandriving.assets.car import Car
from gym_urbandriving.assets.primitives.rectangle import Rectangle
from gym_urbandriving.assets.primitives.circle import Circle
from gym_urbandriving.assets.primitives.shape import Shape
import sys
import pygame
import time
import numpy as np

class PyGameVisualizer:
    """
    pygame visualizer class renders any state passed into it through render using pygame
    """
    def __init__(self, screen_dim):
        pygame.init()
        self.screen_dim = screen_dim
        self.surface = pygame.display.set_mode(screen_dim)
        self.drawfns = {Rectangle:self.draw_rectangle,
                        Circle:self.draw_circle}
        self.static_surface = None

    def render_statics(self, state, valid_area):
        """
        renders static objects of the state
        """
        if self.static_surface:
            self.surface.blit(self.static_surface, (0, 0))
            return

        self.static_surface = pygame.Surface((valid_area[1] - valid_area[0],
                                              valid_area[3] - valid_area[2]))
        for obj in state.static_objects:
            self.drawfns[obj.primitive](obj, self.static_surface)

        self.static_surface = pygame.transform.scale(self.static_surface,
                                                     (self.screen_dim))

        self.surface.blit(self.static_surface, (0, 0))
        return

    def render_dynamics(self, state, valid_area):
        """
        renders dynamic objects of the state
        """
        new_surface = pygame.Surface((valid_area[1] - valid_area[0],
                                      valid_area[3] - valid_area[2]),
                                     pygame.SRCALPHA)
        for obj in state.dynamic_objects:
            self.drawfns[obj.primitive](obj, new_surface)

        new_surface = pygame.transform.scale(new_surface, (self.screen_dim))
        self.surface.blit(new_surface, (0, 0), None)
        return
    
    def render(self, state, valid_area, rerender_statics=False):
        if (rerender_statics):
            self.static_surface = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()


        self.render_statics(state, valid_area)
        self.render_dynamics(state, valid_area)

        pygame.display.flip()

    def draw_rectangle(self, rect, surface):
        obj = pygame.image.load(rect.sprite)
        obj = pygame.transform.scale(obj, (rect.xdim, rect.ydim))

        if rect.angle == 0:
            pos = (rect.x - rect.xdim/2, rect.y - rect.ydim/2)
        else:
            corners = rect.get_corners()
            x_off = min(corners[:,0])
            y_off = min(corners[:,1])
            pos = (x_off, y_off)
            obj = pygame.transform.rotate(obj, rect.angle)
        surface.blit(obj, pos)
        
        for c in rect.get_corners():
            pygame.draw.circle(surface, (255, 0, 255), c.astype(int), 5)
        return

    def draw_circle(self, circ, surface):
        obj = pygame.image.load(circ.sprite)
        obj = pygame.transform.scale(obj, (circ.radius*2, circ.radius*2))
        obj = pygame.transform.rotate(obj, circ.angle)
        surface.blit(obj, (circ.x-circ.radius,circ.y-circ.radius))
        return
