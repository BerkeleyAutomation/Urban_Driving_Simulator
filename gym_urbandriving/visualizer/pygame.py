from gym_urbandriving.assets.car import Car
from gym_urbandriving.assets.primitives import *
import sys
import pygame
import time

class PyGameVisualizer:
    def __init__(self, screen_dim):
        pygame.init()
        self.screen_dim = screen_dim
        self.surface = pygame.display.set_mode(screen_dim)
    def render(self, state, valid_area):

        new_surface = pygame.Surface((valid_area[1] - valid_area[0],
                                      valid_area[3] - valid_area[2]))
        new_surface.set_alpha(255)
        new_surface.fill((255, 255, 255))
        
        for obj in state.get_static_objects():
            if (obj.get_primitive() is Rectangle):
                self.draw_rect(obj, new_surface)
            else:
                print("ERROR")

        for obj in state.get_dynamic_objects():
            if (obj.get_primitive() is Rectangle):
                self.draw_rect(obj, new_surface)
            else:
                print("ERROR")
        new_surface = pygame.transform.scale(new_surface, (self.screen_dim))
        self.surface.blit(new_surface, (0, 0))
        pygame.display.flip()

    def draw_rect(self, rect, surface):
        obj = pygame.image.load(rect.sprite)
        obj = pygame.transform.scale(obj, (rect.xdim, rect.ydim))
        obj = pygame.transform.rotate(obj, rect.angle)
        surface.blit(obj, [rect.x, rect.y])
        return



# if __name__ == "__main__":
#     car = Car(100,200, vel=10)
#     state = [car]
#     vis = Simple_Visualizer(1000,1000)


#     while(True):
#         vis.render(state)
#         for obj in state:
#             obj.step((20,0))
