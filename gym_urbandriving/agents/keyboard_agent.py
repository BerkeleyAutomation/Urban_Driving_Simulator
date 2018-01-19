import pygame
import numpy as np

class KeyboardAgent:
    """
    Agent which interprets user keyboard inputs

    Attributes
    ----------
    agent_num : int
        Index of this agent in the world.
        Used to access its object in state.dynamic_objects
    """
    def __init__(self, agent_num=0):
        self.agent_num = agent_num
        self.target_steer = None
        return
        
    def eval_policy(self, state):
        """
        Returns action based on keyboard input

        Parameters
        ----------
        state : PositionState
            State of the world, unused

        Returns
        -------
        action
            Keyboard action
        """

        obj = state.dynamic_objects[self.agent_num]

        ac2 = np.arctan2(500.0-obj.y, 500-obj.x)

        self.target_steer = ac2-np.radians(obj.angle) if ac2-np.radians(obj.angle) >=  -np.pi else ac2-np.radians(obj.angle)+2*np.pi

        print ac2, np.radians(obj.angle), self.target_steer
        print state.dynamic_objects[self.agent_num].x, state.dynamic_objects[self.agent_num].y, state.dynamic_objects[self.agent_num].angle

        steer, acc = 0, 0
        pygame.event.pump()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            acc = 1
        elif keys[pygame.K_DOWN]:
            acc = -1
        if keys[pygame.K_LEFT]:
            steer = 3
        elif keys[pygame.K_RIGHT]:
            steer = -3


        return (self.target_steer, acc)

