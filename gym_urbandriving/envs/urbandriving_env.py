import gym
from copy import deepcopy
from gym_urbandriving.agents import *
import numpy as np
import ray

@ray.remote
class RayNode:
    def __init__(self, agent_type, agent_num):
        self.agent = agent_type(agent_num)

    def eval_policy(self, state):
        return self.agent.eval_policy(state)
class UrbanDrivingEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self,
                 init_state,
                 visualizer=None,
                 reward_fn=lambda x: 0,
                 max_time=500,
                 bgagent=NullAgent,
                 randomize=False,
                 use_ray=False):
        self.visualizer = visualizer
        self.reward_fn = reward_fn
        self.init_state = deepcopy(init_state)
        self.bgagent_type = bgagent
        self.max_time = max_time
        self.time = 0
        self.randomize = randomize
        self.statics_rendered = False
        self.use_ray = use_ray
        if use_ray:
            ray.init()
        self.dynamic_collisions, self.static_collisions, self.last_col = [], [], -1
        if (self.init_state):
            self._reset()

    def get_collisions(self):
        if self.last_col == self.time:
            return self.dynamic_collisions, self.static_collisions
        self.dynamic_collisions, self.static_collisions = self.current_state.get_collisions()
        self.last_col = self.time
        return self.dynamic_collisions, self.static_collisions

    def collides_any(self, agentnum):
        self.get_collisions()
        for coll in self.dynamic_collisions:
            if agentnum in coll:
                return True
        for coll in self.static_collisions:
            if agentnum == coll[0]:
                return True
        return False

    
    def _step(self, action, agentnum=0):
        assert(self.current_state is not None)
        # Get actions for all objects
        actions = [None]*len(self.current_state.dynamic_objects)
        actions[agentnum] = action

        if self.use_ray:
            assert(all([type(bgagent) == RayNode for i, bgagent in self.bg_agents.items()]))
            stateid = ray.put(self.get_state_copy())
            actionids = {}
            for i, agent in self.bg_agents.items():
                if i is not agentnum:
                    actionids[i] = agent.eval_policy.remote(stateid)
            for i, aid in actionids.items():
                action = ray.get(aid)
                actions[i] = action
        else:
            assert(all([type(bgagent) != RayNode for i, bgagent in self.bg_agents.items()]))
            for i, agent in self.bg_agents.items():
                if i is not agentnum:
                    actions[i] = agent.eval_policy(self.get_state_copy())
        for i, dobj in enumerate(self.current_state.dynamic_objects):
            dobj.step(actions[i])

        self.time += 1
        dynamic_coll, static_coll = self.get_collisions()
        state = self.get_state_copy()
        reward = self.reward_fn(self.current_state)
        done = (self.time == self.max_time) or len(dynamic_coll) or len(static_coll)

        predict_accuracy = None
        if self.bgagent_type == ModelAgent:
            predict_accuracy = sum([o.score for o in self.bg_agents])/len(self.bg_agents)

        info_dict = {"dynamic_collisions":dynamic_coll,
                     "static_collisions":static_coll,
                     "saved_actions": actions,
                     "predict_accuracy": predict_accuracy}
 
        return state, reward, done, info_dict


    def _reset(self, new_state=None):
        self.last_col = -1
        if new_state:
            self.init_state = new_state
            self.statics_rendered = False
        self.time = 0
        if self.randomize:
            self.init_state.randomize()
        self.current_state = deepcopy(self.init_state)
        if self.use_ray:
            self.bg_agents = {i: RayNode.remote(self.bgagent_type, i) \
                              for i in range(len(self.current_state.dynamic_objects))}
        else:
            self.bg_agents = {i: self.bgagent_type(i) \
                              for i in range(len(self.current_state.dynamic_objects))}
        return

    def _render(self, mode='human', close=False, waypoints=[]):
        if close:
            return
        if self.visualizer:
            window = [0, self.current_state.dimensions[0],
                      0, self.current_state.dimensions[1]]
            self.get_collisions()
            self.visualizer.render(self.current_state, window,
                                   self.dynamic_collisions, self.static_collisions,
                                   rerender_statics=not self.statics_rendered,
                                   waypoints=waypoints)
            self.statics_rendered = True

    def get_state_copy(self):
        return deepcopy(self.current_state)
