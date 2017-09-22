from gym_urbandriving.assets.car import Car
import sys
import pygame
import time

class Visualizer:

    def __init__(self):
        pass
    def render():
        pass

class Simple_Visualizer(Visualizer):
    def __init__(self, screen_width, screen_height):
        pygame.init()
        self.surface = pygame.display.set_mode([screen_width,screen_height])


    def render(self,state):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()


        self.surface.fill((255,255,255))
        for obj in state:
            x, y, x_dim, y_dim, angle= obj.get_state()
            car = pygame.image.load("gym_urbandriving/visualizer/sprites/blue_car_lite.png")
            car = pygame.transform.rotate(car,angle)
            self.surface.blit(car,[x-x_dim/2, y-y_dim/2])
            
        pygame.display.flip()

            


if __name__ == "__main__":
    car = Car(100,200, vel=10)
    state = [car]
    vis = Simple_Visualizer(1000,1000)
    

    while(True):
        vis.render(state)
        for obj in state:
            obj.step((20,0))

