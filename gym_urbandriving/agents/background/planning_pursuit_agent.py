import numpy as np
from gym_urbandriving.utils import PIDController
from gym_urbandriving.agents import PursuitAgent
from gym_urbandriving.planning import VelocityMPCPlanner,GeometricPlanner
import gym_urbandriving as uds

class PlanningPursuitAgent(PursuitAgent):
    """
    Background agent which implements the full plannning stack given known behavioral logic. 
    The planner first generates a nominal trajecotry, then at each timestep
    plans its velocity to avoid collisons. 

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
            The number which specifies the agent in the dictionary state.dynamic_objects['background_cars']

        """
        self.agent_num = agent_num
        #Move to JSON 
        self.PID_acc = PIDController(1.0, 0, 0)
        self.PID_steer = PIDController(2.0, 0, 0)
        self.not_initiliazed = True
        self.count = 0

        
        

        
    def eval_policy(self, state,simplified = False):
        """
        Returns action based on current state

        Parameters
        ----------
        state : PositionState
            State of the world, unused

        Returns
        -------
        tuple with floats (steering,acceleration)
        """
     
        if self.not_initiliazed:
            
            geoplanner = GeometricPlanner(state, inter_point_d=40.0, planning_time=0.1)

            geoplanner.plan_for_agents(state,type_of_agent='background_cars',agent_num=self.agent_num)
            self.not_initiliazed = False
            print("MADE PLAN")
            print(simplified)

        if not simplified:
            target_vel = VelocityMPCPlanner().plan(state, self.agent_num)
            state.dynamic_objects['background_cars'][str(self.agent_num)].trajectory.set_vel(target_vel)

        action = super(PlanningPursuitAgent, self).eval_policy(state)
        return action

