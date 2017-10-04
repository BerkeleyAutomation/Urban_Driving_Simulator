from gym_urbandriving.state import PositionState


from copy import deepcopy
import numpy as np

class AccelAgent:
    def __init__(self, agent_num=0):
        self.agent_num = agent_num
        return
    
    def eval_policy(self, state, nsteps=7):
        """
        If we can accelerate, see if we crash in nsteps.
        If we crash, decelerate, else accelerate
        """
        from gym_urbandriving import UrbanDrivingEnv
        planning_env = UrbanDrivingEnv(init_state=state)

        planning_env._reset()
        next_state, r, done, info_dict = planning_env._step((0, 1),
                                                            self.agent_num,
                                                            copy_state=False)
        for i in range(nsteps):
            next_state, r, done, info_dict = planning_env._step(None,
                                                                self.agent_num,
                                                                copy_state=False)
            if (done and next_state.collides_any(self.agent_num)):
                return (0, -1)
        return (0,1)
