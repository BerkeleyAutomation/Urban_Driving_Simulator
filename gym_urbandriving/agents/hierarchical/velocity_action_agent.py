import numpy as np
from gym_urbandriving.utils import PIDController
from gym_urbandriving.agents import PursuitAgent
from gym_urbandriving.planning import VelocityMPCPlanner,GeometricPlanner
import gym_urbandriving as uds

from gym_urbandriving.actions import VelocityAction

class VelocityActionAgent(PursuitAgent):
    """
    Hierarichal agent which implements the full plannning stack except the velocity component
    The planner first generates a nominal trajecotry, then at each timestep recives a target velocity
    to track with PID controller. 


    Attributes
    ----------
    agent_num : int
        Index of this agent in the world.
        Used to access its object in state.dynamic_objects

    """

    def __init__(self, agent_num=0):
        """
        Initializes the VelocityActionAgent Class

        Parameters
        ----------
        agent_num: int
            The number which specifies the agent in the dictionary state.dynamic_objects['controlled_cars']

        """

        self.agent_num = agent_num
        #Move to JSON 
        self.PID_acc = PIDController(1.0, 0, 0)
        self.PID_steer = PIDController(2.0, 0, 0)
        self.not_initiliazed = True
        

        
    def eval_policy(self, action,state,simplified = False):
        """
        Returns action based next state in trajectory. 

        Parameters
        ----------
        state : PositionState
            State of the world, unused
        action : VelocityAction or None
            Target velocity for car to travel at 

        Returns
        -------
        tuple with floats (steering,acceleration)
        """

        if not (isinstance(action,VelocityAction) or action == None):
           raise Exception('Action is not of type VelocityAction')

        if not state.dynamic_objects["controlled_cars"][str(self.agent_num)].trajectory:
            geoplanner = GeometricPlanner(state, inter_point_d=40.0, planning_time=0.1)

            geoplanner.plan_for_agents(state,type_of_agent='controlled_cars',agent_num=self.agent_num)
            self.not_initiliazed = False

        if not simplified:
            target_vel = action
            state.dynamic_objects['controlled_cars'][str(self.agent_num)].trajectory.set_vel(target_vel)

        return super(VelocityActionAgent, self).eval_policy(state,type_of_agent='controlled_cars')


