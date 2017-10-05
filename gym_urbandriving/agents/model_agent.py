from gym_urbandriving.state import PositionState
from sklearn import linear_model
import pickle

from copy import deepcopy
import numpy as np

class ModelAgent:
    def __init__(self, agent_num=0):
        self.agent_num = agent_num
        self.model = pickle.load(open("model.model", "rb"))
        self.correct = 0
        self.ticks = 0
        return
    
    def vectorize_state(self, state):
        state_vec = []
        for obj in state.dynamic_objects:
            state_vec.append((obj.x-500)/500)
            state_vec.append((obj.y-500)/500)
            state_vec.append((obj.vel-10)/10)
            state_vec.append(obj.angle/180)
        return state_vec

    
    def eval_policy(self, state, nsteps=8):
        """
        If we can accelerate, see if we crash in nsteps.
        If we crash, decelerate, else accelerate
        """

        # Accel agent's prediction
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

        # Our prediction
        pred_class = self.model.predict(np.matrix([[self.agent_num] + self.vectorize_state(state)]))
        our_action = actions[2-pred_class[0]]
        if our_action == best_action:
            self.correct += 1
        self.ticks += 1
        
        return our_action
