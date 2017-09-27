import pygame

class KeyboardAgent:
    def __init__(self, i=0):
        self.i = i
        return
    def eval_policy(self, state):
        steer, acc = 0, 0
        pygame.event.pump()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            acc = 1
        elif keys[pygame.K_DOWN]:
            acc = -1
        if keys[pygame.K_LEFT]:
            steer = 2
        elif keys[pygame.K_RIGHT]:
            steer = -2
        return (steer, acc)
