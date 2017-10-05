import gym
from copy import deepcopy
from gym_urbandriving.state import *
from gym_urbandriving.agents import *
import numpy as np

class UrbanDrivingEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self,
                 init_state,
                 visualizer=None,
                 reward_fn=lambda x: 0,
                 max_time=500,
                 bgagent=NullAgent,
                 randomizer=lambda state: state):
        self.visualizer = visualizer
        self.reward_fn = reward_fn
        self.init_state = init_state
        self.bgagent_type = bgagent
        self.bg_agents = []
        self.max_time = max_time
        self.current_state = PositionState()
        self.time = 0
        self.randomizer = randomizer

        self._reset()

        self.current_state = deepcopy(self.init_state)
        assert(self.init_state is not None)
        assert(self.current_state is not None)

    def _step(self, action, agentnum=0, copy_state=True):
        actions = [None]*len(self.current_state.dynamic_objects)
        actions[agentnum] = action
        self.current_state.reset_collisions()

        for i in range(1, len(self.current_state.dynamic_objects)):
            actions[i] = self.bg_agents[i].eval_policy(self.current_state,)
        actions[agentnum] = action
        for i, dynamic_object in enumerate(self.current_state.dynamic_objects):
            dynamic_object.step(actions[i])


        self.time += 1
        dynamic_coll, static_coll = self.current_state.get_collisions()
        if copy_state:
            state = self.get_state_copy()
        else:
            state = self.current_state
        reward = self.reward_fn(self.current_state)
        done = (self.time > self.max_time) or len(dynamic_coll) or len(static_coll)

        info_dict = {"dynamic_collisions":dynamic_coll,
                     "static_collisions":static_coll,
                     "saved_actions":actions}
 
        return state, reward, done, info_dict


    def _reset(self):
        self.time = 0
        self.init_state = self.randomizer(self.init_state)
        self.current_state = deepcopy(self.init_state)
        assert(self.current_state is not None)
        self.bg_agents = [self.bgagent_type(i) \
                          for i, dynamic_object in \
                          enumerate(self.current_state.dynamic_objects)]
        return

    def _render(self, mode='human', close=False):
        if close:
            return
        if self.visualizer:
            self.visualizer.render(self.current_state, [0, self.current_state.dimensions[0],
                                                        0, self.current_state.dimensions[1]])

    def get_state_copy(self, state_type=PositionState):
        if state_type == PositionState:
            return deepcopy(self.current_state)
        elif state_type == None:
            return None
