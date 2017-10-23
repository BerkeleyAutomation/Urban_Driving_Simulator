import pygame

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
        return (steer, acc)
