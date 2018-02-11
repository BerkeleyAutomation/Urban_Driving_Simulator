import numpy as np
from gym_urbandriving.utils.PID import PIDController

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
        self.PID_acc = PIDController(1.0, .1, 0)
        self.PID_steer = PIDController(2, 0, 0)
        
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

        if not obj.trajectory.is_empty():
            target_loc = obj.trajectory.pop()[:2].tolist()
            target_vel = 5
        else:
            target_loc = obj.destination
            target_vel = 5

        ac2 = np.arctan2(obj.y-target_loc[1], target_loc[0]-obj.x)

        ang = obj.angle if obj.angle<np.pi else obj.angle-2*np.pi
        
        e_angle = ac2-ang
        if e_angle > np.pi:
            e_angle -= (np.pi*2)
        elif e_angle < -np.pi:
            e_angle += (np.pi*2)

        e_vel = target_vel-obj.vel

        action_acc = self.PID_acc.get_control(e_vel)
        action_steer = self.PID_steer.get_control(e_angle)
        return (action_steer, action_acc)