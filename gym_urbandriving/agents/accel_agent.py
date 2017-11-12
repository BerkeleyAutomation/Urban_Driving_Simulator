from copy import deepcopy
import numpy as np

class AccelAgent:
    """
    Simple greedy search agent. Chooses action which maximizes expected time
    collision

    Attributes
    ----------
    actions : list
        Set of actions to choose from
    agent_num : int
        Index of this agent in the world.
        Used to access its object in state.dynamic_objects
    planning_env : UrbanDrivingEnv
        World simulator used internally to plan
    """
    actions = [(0, 1), (2, 1), (-2, 1), (0, 0), (1, -1), (-1, -1)]
    def __init__(self, agent_num=0):
        self.agent_num = agent_num
        from gym_urbandriving import UrbanDrivingEnv
        self.planning_env = UrbanDrivingEnv(init_state=None)
        return

    def eval_policy(self, state, nsteps=8):
        """
        Chooses best action for this agent in the state.
        Looks forward nsteps to evaluate best action

        Parameters
        ----------
        state : PositionState
            State of the world,
            with this agent controlling state.dynamic_objects[self.agent_num]
        nsteps : int
            How many steps forward to look in planning

        Returns
        -------
        action
            Best action
        """
        self.planning_env._reset(state)
        start_pos = state.dynamic_objects[self.agent_num].get_pos()
        best_action = None
        best_time = 0
        best_distance = 0
        for action in self.actions:
            self.planning_env._reset()
            pos = state.dynamic_objects[self.agent_num].get_pos()
            dist_to_coll = state.min_dist_to_coll(self.agent_num)
            next_state, r, done, info_dict = self.planning_env._step(action,
                                                                self.agent_num)
            delta_x = next_state.dynamic_objects[self.agent_num].get_pos()
            delta_x = next_state.min_dist_to_coll(self.agent_num) + next_state.dynamic_objects[self.agent_num].vel
            # for i in range(nsteps):
            #     next_state, r, done, info_dict = self.planning_env._step(action,
            #                                                         self.agent_num)
            #     time = self.planning_env.time
            #     if (done and next_state.collides_any(self.agent_num)):
            #         break
            
            # if time == nsteps + 1:
            #     return action
            # if time > best_time:
            #     best_action = action
            #     best_time = time
            if delta_x > best_distance:
                best_action = action
                best_distance = delta_x
        return best_action
