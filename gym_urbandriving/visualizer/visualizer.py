import sys
import pygame
import time

class Visualizer:

    def __init__(self):
        pass
    def render():
        pass

class Simple_Visualizer(Visualizer):
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode([500,500])


    def render(self,state):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()


        self.surface.fill((255,255,255))
        for obj in state:
            car = pygame.image.load("sprites/blue_car_lite.png")
            car = pygame.transform.rotate(car,obj[2])
            self.surface.blit(car,[obj[0]-car.get_width()/2, obj[1]-car.get_height()/2])
            
        pygame.display.flip()

            


if __name__ == "__main__":
    state = [[0,0,0],[100,300,90]]
    vis = Simple_Visualizer()
    

    while(True):
        vis.render(state)
        state[0][0] += 1
        state[0][1] += 1
        state[1][2] += 10


