import numpy as np
from gym_urbandriving.utils.PID import PIDController

class PursuitAgent:
    """
    Agent which uses PID to implement a pursuit control policy
    Uses a trajectory with x,y,v,-

    Attributes
    ----------
    agent_num : int
        Index of this agent in the world.
        Used to access its object in state.dynamic_objects
    """
    def __init__(self, agent_num=0):
        self.agent_num = agent_num
        self.PID_acc = PIDController(1.0, 0, 0)
        self.PID_steer = PIDController(2.0, 0, 0)
        
    def eval_policy(self, state):
        """
        Returns action based next state in trajectory. 

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
            p = obj.trajectory.first()
            target_loc = p[:2].tolist()
            target_vel = p[2]

            while (((obj.y-p[1])**2+(p[0]-obj.x)**2)<100):
                p = obj.trajectory.pop()
                target_loc = p[:2].tolist()
                target_vel = p[2]
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
        e_vel_ = np.sqrt((obj.y-target_loc[1])**2+(target_loc[0]-obj.x)**2) - obj.vel


        action_acc = self.PID_acc.get_control(e_vel)
        action_steer = self.PID_steer.get_control(e_angle)


        return (action_steer, action_acc)