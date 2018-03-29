import numpy as np
from gym_urbandriving.utils.PID import PIDController
from gym_urbandriving.agents import PursuitAgent
from gym_urbandriving.planning import VelocityMPCPlanner,GeometricPlanner
from copy import deepcopy
import gym_urbandriving as uds

class PlanningPursuitAgent(PursuitAgent):
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
        #Move to JSON 
        self.PID_acc = PIDController(1.0, 0, 0)
        self.PID_steer = PIDController(2.0, 0, 0)
        self.not_initiliazed = True
        self.count = 0

        
        

        
    def eval_policy(self, state,simplified = False):
        """
        Returns action based next state in trajectory. 

        Parameters
        ----------
        state : PositionState
            State of the world, unused
        """
     
        if self.not_initiliazed:
            
            geoplanner = GeometricPlanner(deepcopy(state), inter_point_d=40.0, planning_time=0.1)

            geoplanner.plan_for_agents(state,type_of_agent='background_cars',agent_num=self.agent_num)
            self.not_initiliazed = False
            print("MADE PLAN")
            print(simplified)

        if not simplified:
            target_vel = VelocityMPCPlanner().plan(deepcopy(state), self.agent_num)
            state.dynamic_objects['background_cars'][str(self.agent_num)].trajectory.set_vel(target_vel)

        action = super(PlanningPursuitAgent, self).eval_policy(state)
      
        return action

