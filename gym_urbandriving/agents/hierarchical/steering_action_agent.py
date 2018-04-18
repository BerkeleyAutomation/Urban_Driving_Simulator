import numpy as np
from gym_urbandriving.utils import PIDController
from gym_urbandriving.agents import PursuitAgent
from gym_urbandriving.planning import VelocityMPCPlanner,GeometricPlanner
import gym_urbandriving as uds
from gym_urbandriving.actions import SteeringAction

class SteeringActionAgent(PursuitAgent):
    """
    Hierarichal agent which does not include any planning stack and only requires 
    specifiying the steering agent.  

    Attributes
    ----------
    agent_num : int
        Index of this agent in the world.
        Used to access its object in state.dynamic_objects

    """

    def __init__(self, agent_num=0):
        """
        Initializes the PlanningPursuitAgent Class

        Parameters
        ----------
        agent_num: int
            The number which specifies the agent in the dictionary state.dynamic_objects['controlled_cars']

        """
        self.agent_num = agent_num
        self.PID_acc = PIDController(1.0, 0, 0)
        self.PID_steer = PIDController(2.0, 0, 0)
        self.not_initiliazed = True
        

        
    def eval_policy(self, action,state,simplified=False):
        """
        Returns action based next state in trajectory. 

        Parameters
        ----------
        state : PositionState
            State of the world, unused
        action : SteeringAction
            

        Returns
        -------
        tuple with floats (steering,acceleration)
        """
        
        

        if simplified:
            return SteeringAction(0.0,0.0)

        if not isinstance(action,SteeringAction):
            raise Exception('Actions is Not of Type Steering Action')

        return action


