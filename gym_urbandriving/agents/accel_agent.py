from copy import deepcopy
import numpy as np
import ray

@ray.remote
class AccelAgent:
    actions = [(0, 1), (2, 1), (-2, 1), (0, 0), (1, -1), (-1, -1)]
    def __init__(self, agent_num=0):
        self.agent_num = agent_num
        from gym_urbandriving import UrbanDrivingEnv
        self.planning_env = UrbanDrivingEnv(init_state=None)
        return
    
    def eval_policy(self, state, nsteps=8):
        """
        If we can accelerate, see if we crash in nsteps.
        If we crash, decelerate, else accelerate
        """

        self.planning_env._reset(state)
        start_pos = state.dynamic_objects[self.agent_num].get_pos()
        best_action = None
        best_time = 0
        best_distance = 0
        for action in self.actions:
            self.planning_env._reset()
            next_state, r, done, info_dict = self.planning_env._step(action,
                                                                self.agent_num)
            success = True
            for i in range(nsteps):
                next_state, r, done, info_dict = self.planning_env._step(action,
                                                                    self.agent_num)
                time = self.planning_env.time
                if (done and self.planning_env.collides_any(self.agent_num)):
                    break

            if time == nsteps + 1:
                return action
            if time > best_time:
                best_action = action
                best_time = time
        return best_action
