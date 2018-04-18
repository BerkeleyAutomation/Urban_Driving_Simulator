import numpy as np
from gym_urbandriving.utils import PIDController
from gym_urbandriving.agents import Agent
from gym_urbandriving.actions import SteeringAction

class PursuitAgent(Agent):
    
    def __init__(self, agent_num=0):
        """
        Initializes the PlanningPursuitAgent Class

        Parameters
        ----------
        agent_num: int
            The number which specifies the agent in the dictionary state.dynamic_objects['background_cars']

        """
        self.agent_num = agent_num
        self.PID_acc = PIDController(1.0, 0, 0)
        self.PID_steer = PIDController(2.0, 0, 0)
        
    def eval_policy(self, state,type_of_agent = 'background_cars'):
        """
        Returns action based next state in trajectory. 

        Parameters
        ----------
        state : PositionState
            State of the world, unused

        Returns
        -------
        SteeringAction
        """

        obj = state.dynamic_objects[type_of_agent][str(self.agent_num)]

        if not obj.trajectory.is_empty():    
            p = obj.trajectory.first()
            target_loc = p[:2].tolist()
            target_vel = p[2]

            while obj.contains_point((p[0], p[1])) and not obj.trajectory.is_empty():
                p = obj.trajectory.pop()
                target_loc = p[:2].tolist()
                target_vel = p[2]

        else:
            return SteeringAction(steering=0.0, acceleration=0.0)


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


        return SteeringAction(steering=action_steer, acceleration=action_acc)
