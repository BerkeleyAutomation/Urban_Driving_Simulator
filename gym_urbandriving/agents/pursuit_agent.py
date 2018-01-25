import pygame
import numpy as np

class PursuitAgent:
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
 
        if self.target_loc_index >= len(self.target_locs):
            return (0,0)

        if np.linalg.norm(np.array([obj.x, obj.y])-np.array(self.target_locs[self.target_loc_index]))<5:
            self.target_loc_index += 1

        if self.target_loc_index >= len(self.target_locs):
            return (0,0)

        target = self.target_locs[self.target_loc_index]
        ac2 = np.arctan2(obj.y-target[1], target[0]-obj.x)

        ang = obj.angle if obj.angle<np.pi else obj.angle-2*np.pi
        
        res_angle = ac2-ang
        if res_angle > np.pi:
            res_angle -= (np.pi*2)
        elif res_angle < -np.pi:
            res_angle += (np.pi*2)

        res = np.degrees(res_angle)/10
        acc = np.random.uniform(-2,3)
        #print (res,acc)

        return (res, 3)