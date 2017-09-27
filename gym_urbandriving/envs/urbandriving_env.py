import gym
from copy import deepcopy
from gym_urbandriving.state import *
from gym_urbandriving.agents import *
import numpy as np

class UrbanDrivingEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, visualizer=None, init_state=None,
                 reward_fn=lambda x: 0, max_time=500,
                 bgagent=NullAgent):
        self.visualizer = visualizer
        self.reward_fn = reward_fn
        self.init_state = init_state
        self.bg_agents = []
        self.max_time = max_time
        self.current_state = PositionState()
        self.time = 0

        self._reset()

        self.current_state = deepcopy(self.init_state)
        assert(self.init_state is not None)
        assert(self.current_state is not None)

    def _step(self, action, agentnum=0, state_type=PositionState):
        actions = [None]*len(self.current_state.dynamic_objects)
        actions[agentnum] = action

        for i in range(1, len(self.current_state.dynamic_objects)):
            actions[i] = self.bg_agents[i].eval_policy(self.current_state,)

        for i, dynamic_object in enumerate(self.current_state.dynamic_objects):
            dynamic_object.step(actions[i])

        self.time += 1

        state = self.get_state_copy(state_type=state_type)
        reward = self.reward_fn(self.current_state)
        done = (self.time > self.max_time) or self.current_state.done()
        return state, reward, done


    def _reset(self):
        self.time = 0
        self.current_state = deepcopy(self.init_state)
        assert(self.current_state is not None)
        self.bg_agents = [NullAgent(i) \
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
        elif state_type == RenderState:
            return RenderState(self.current_state)
