import gym
from copy import deepcopy
from gym_urbandriving.state import *
from gym_urbandriving.assets import *
from gym_urbandriving.agents import *

class UrbanDrivingEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, visualizer=None, init_state=None,
                 reset_random=True, reward_fn=lambda x: 0, max_time=10000):
        self.visualizer = visualizer
        self.reward_fn = reward_fn
        self.init_state = init_state
        self.bg_agents = []
        self.max_time = max_time
        self.reset_random = reset_random
        self.current_state = PositionState()


        if not self.init_state:
            self._reset()

        self.current_state = deepcopy(self.init_state)
        assert(self.init_state is not None)
        assert(self.current_state is not None)

    def _step(self, action, state_type=PositionState):
        actions = [None]*len(self.current_state.dynamic_objects)
        actions[0] = action

        for i in range(1, len(self.current_state.dynamic_objects)):
            actions[i] = self.bg_agents[i].eval_policy(self.current_state,)

        for i, dynamic_object in enumerate(self.current_state.dynamic_objects):
            dynamic_object.step(actions[i])

        self.time += 1

        state = self.get_state_copy(state_type=state_type)
        reward = self.reward_fn(self.current_state)
        done = (self.time > self.max_time) or self.done()
        return state, reward, done

    def done(self):
        return self.current_state.has_collisions() or self
    def _reset(self):
        self.time = 0
        if self.reset_random:
            self.init_state = PositionState()
            self.init_state.terrain_objects.extend([Terrain(0, 0, 400, 400),
                                                    Terrain(600, 0, 400, 400),
                                                    Terrain(0, 600, 400, 400),
                                                    Terrain(600, 600, 400, 400)])
            self.init_state.street_objects.extend([Street(400, 0, 200, 1000),
                                                   Street(0, 400, 1000, 200)])
            self.init_state.dynamic_objects.append(Car(500, 100, angle=-90, vel=5))
            self.init_state.dynamic_objects.append(KinematicCar(100, 500, vel=5))

        self.current_state = deepcopy(self.init_state)
        assert(self.current_state is not None)
        self.bg_agents = [BackgroundAgent(type(dynamic_object), i)\
                          for i, dynamic_object in\
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
