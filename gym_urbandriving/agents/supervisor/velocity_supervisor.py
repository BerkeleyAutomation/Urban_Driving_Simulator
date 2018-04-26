import numpy as np
from gym_urbandriving.utils import PIDController
from gym_urbandriving.agents import PursuitAgent
from gym_urbandriving.planning import VelocityMPCPlanner,GeometricPlanner
import gym_urbandriving as uds

class VelocitySupervisor(PursuitAgent):
    """
    Superivsor agent which implements the planning stack to obtain velocity level supervision of
    which the car should follow. 

    Attributes
    ----------
    agent_num : int
        Index of this agent in the world.
        Used to access its object in state.dynamic_objects

    """

    def __init__(self, agent_num=0):
        """
        Initializes the VelocitySupervisor Class

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
        
        

        
    def eval_policy(self, state,simplified = False):
        """
        Returns action based next state in trajectory. 

        Parameters
        ----------
        state : PositionState
            State of the world, unused

        simplified: bool
            specifies whether or not to use a simplified greedy model for look ahead planning

        Returns
        --------
        float specifying target velocity
        """

        if self.not_initiliazed:
            geoplanner = GeometricPlanner(state, inter_point_d=40.0, planning_time=0.1)

            geoplanner.plan_for_agents(state,type_of_agent='controlled_cars',agent_num=self.agent_num)
            self.not_initiliazed = False
           

       
        target_vel = VelocityMPCPlanner().plan(state, self.agent_num, type_of_agent = "controlled_cars")

            
            

        return target_vel


