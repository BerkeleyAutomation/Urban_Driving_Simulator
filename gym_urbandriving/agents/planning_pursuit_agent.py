import numpy as np
from gym_urbandriving.utils.PID import PIDController
from gym_urbandriving.agents import PursuitAgent
from gym_urbandriving.planning import VelocityMPCPlanner
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



        target_vel = VelocityMPCPlanner().plan(deepcopy(state), self.agent_num)
        if target_vel == 4:
            state.dynamic_objects[self.agent_num].trajectory.restart()
        elif target_vel == 0:
            state.dynamic_objects[self.agent_num].trajectory.modify_to_stop()
        else:
            pass

        return super(PlanningPursuitAgent, self).eval_policy(state)


