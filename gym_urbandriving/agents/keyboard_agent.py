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
        self.target_locs = [(600,450), (475,475), (450,600), (450,900)]
        self.target_loc_index = 0
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
        """
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
        """

        if self.target_loc_index >= len(self.target_locs):
            return (0,0)

        if np.linalg.norm(np.array([obj.x, obj.y])-np.array(self.target_locs[self.target_loc_index]))<5:
            print 'moving on'
            self.target_loc_index += 1

        if self.target_loc_index >= len(self.target_locs):
            return (0,0)

        target = self.target_locs[self.target_loc_index]
        ac2 = np.arctan2(obj.y-target[1], target[0]-obj.x)

        ang = np.radians(obj.angle) if obj.angle<180 else np.radians(obj.angle-360)
        
        res_angle = ac2-ang
        if res_angle > np.pi:
            res_angle -= (np.pi*2)
        elif res_angle < -np.pi:
            res_angle += (np.pi*2)

        res = np.degrees(res_angle)/10
        acc = np.random.uniform(-2,3)
        #print (res,acc)

        return (res, 1)

