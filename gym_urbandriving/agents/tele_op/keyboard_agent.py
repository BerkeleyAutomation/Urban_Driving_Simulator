import pygame
from gym_urbandriving.agents import Agent
from gym_urbandriving.actions import SteeringAction
import numpy as np

class KeyboardAgent(Agent):
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
        numpy array with elements (steering,acceleration)
        """
        steer, acc = 0, 0
        try:
            pygame.event.pump()
        except pygame.error:
            print("Error: Needs a visualizer")
            return (0, 0)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            acc = 1
        elif keys[pygame.K_DOWN]:
            acc = -1
        if keys[pygame.K_LEFT]:
            steer = 1
        elif keys[pygame.K_RIGHT]:
            steer = -1
        return SteeringAction(steer, acc)
