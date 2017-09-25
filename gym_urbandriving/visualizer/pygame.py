from gym_urbandriving.assets.car import Car
from gym_urbandriving.assets.primitives import *
import sys
import pygame
import time
import numpy as np

class PyGameVisualizer:
    def __init__(self, screen_dim):
        pygame.init()
        self.screen_dim = screen_dim
        self.surface = pygame.display.set_mode(screen_dim)
        self.drawfns = {Rectangle:self.draw_rectangle,
                        Circle:self.draw_circle}
        
    def render(self, state, valid_area):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        new_surface = pygame.Surface((valid_area[1] - valid_area[0],
                                      valid_area[3] - valid_area[2]))
        new_surface.set_alpha(255)
        new_surface.fill((255, 255, 255))


        for obj in state.static_objects:
            self.drawfns[obj.primitive](obj, new_surface)

        for obj in state.dynamic_objects:
            self.drawfns[obj.primitive](obj, new_surface)

        new_surface = pygame.transform.scale(new_surface, (self.screen_dim))
        self.surface.blit(new_surface, (0, 0))

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
        return
    
    def draw_circle(self, circ, surface):
        obj = pygame.image.load(circ.sprite)
        obj = pygame.transform.scale(obj, (circ.radius*2, circ.radius*2))
        obj = pygame.transform.rotate(obj, circ.angle)
        surface.blit(obj, (circ.x-circ.radius,circ.y-circ.radius))
        return



# if __name__ == "__main__":
#     car = Car(100,200, vel=10)
#     state = [car]
#     vis = Simple_Visualizer(1000,1000)


#     while(True):
#         vis.render(state)
#         for obj in state:
#             obj.step((20,0))
