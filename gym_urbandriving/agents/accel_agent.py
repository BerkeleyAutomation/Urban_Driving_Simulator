from gym_urbandriving.state import PositionState


from copy import deepcopy
import numpy as np

class AccelAgent:
    def __init__(self, agent_num=0):
        self.agent_num = agent_num
        return
    
    def eval_policy(self, state, nsteps=8):
        """
        If we can accelerate, see if we crash in nsteps.
        If we crash, decelerate, else accelerate
        """
        from gym_urbandriving import UrbanDrivingEnv
        planning_env = UrbanDrivingEnv(init_state=state)

        actions = [(0, 1), (0, 0), (0, -1)]
        best_action = None
        best_time = 0
        for action in actions:
            planning_env._reset()
            next_state, r, done, info_dict = planning_env._step(action,
                                                                self.agent_num,
                                                                copy_state=False)
            success = True
            for i in range(nsteps):
                next_state, r, done, info_dict = planning_env._step(action,
                                                                    self.agent_num,
                                                                    copy_state=False)
                time = planning_env.time
                if (done and next_state.collides_any(self.agent_num)):
                    break

            if time == nsteps:
                return action
            if time > best_time:
                best_action = action
                best_time = time
        return best_action
