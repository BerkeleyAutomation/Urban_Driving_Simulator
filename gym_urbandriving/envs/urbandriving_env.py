import gym
from copy import deepcopy
from gym_urbandriving.agents import *
import numpy as np
from multiprocessing import Pool, Queue


def agent_update(dobj, agent, state, agentnum):
    action = agent.eval_policy(state)
    dobj.step(action)
    return agentnum, dobj, action

class UrbanDrivingEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self,
                 init_state,
                 visualizer=None,
                 reward_fn=lambda x: 0,
                 max_time=500,
                 bgagent=NullAgent,
                 randomize=False,
                 nthreads=1):
        self.visualizer = visualizer
        self.reward_fn = reward_fn
        self.init_state = init_state
        self.bgagent_type = bgagent
        self.bg_agents = []
        self.max_time = max_time
        self.time = 0
        self.randomize = randomize
        self.nthreads = nthreads
        if (self.nthreads > 1):
            self.thread_pool = Pool(processes=self.nthreads)
        self._reset()

        self.current_state = deepcopy(self.init_state)
        assert(self.init_state is not None)
        assert(self.current_state is not None)

    def _step(self, action, agentnum=0, copy_state=True):
        import time
        actions = [None]*len(self.current_state.dynamic_objects)
        actions[agentnum] = action
        self.current_state.reset_collisions()
        if self.nthreads == 1:
            if self.bgagent_type is not NullAgent:
                t = time.time()
            for i in range(1, len(self.current_state.dynamic_objects)):
                actions[i] = self.bg_agents[i].eval_policy(self.current_state,)
            actions[agentnum] = action
            if self.bgagent_type is not NullAgent:
                print(time.time() - t)
            for i, dynamic_object in enumerate(self.current_state.dynamic_objects):
                dynamic_object.step(actions[i])
        else:
            dobjs = [self.thread_pool.apply_async(agent_update,
                                                  (dobj, agent, self.current_state,
                                                   i)) \
                     for i, (dobj, agent) in enumerate(zip(self.current_state.dynamic_objects,
                                               self.bg_agents)) \
                     if i is not agentnum]
           
            for res in dobjs:
                i, dobj, agent_action = res.get()
                self.current_state.dynamic_objects[i] = dobj
                actions[i] = agent_action
            self.current_state.dynamic_objects[agentnum].step(action)


        self.time += 1
        dynamic_coll, static_coll = self.current_state.get_collisions()
        if copy_state:
            state = self.get_state_copy()
        else:
            state = self.current_state
        reward = self.reward_fn(self.current_state)
        done = (self.time > self.max_time) or len(dynamic_coll) or len(static_coll)

        predict_accuracy = None
        if self.bgagent_type == ModelAgent:
          predict_accuracy = sum([o.score for o in self.bg_agents])/len(self.bg_agents)

        info_dict = {"dynamic_collisions":dynamic_coll,
                     "static_collisions":static_coll,
                     "saved_actions": actions,
                     "predict_accuracy": predict_accuracy}
 
        return state, reward, done, info_dict


    def _reset(self):
        self.time = 0
        if self.randomize:
            self.init_state.randomize()
        self.current_state = deepcopy(self.init_state)
        assert(self.current_state is not None)
        self.bg_agents = [self.bgagent_type(i) \
                          for i, dynamic_object in \
                          enumerate(self.current_state.dynamic_objects)]
        return

    def _render(self, mode='human', close=False, waypoints = []):
        if close:
            return
        if self.visualizer:
            window = [0, self.current_state.dimensions[0],
                      0, self.current_state.dimensions[1]]
            self.visualizer.render(self.current_state, window, waypoints = waypoints)

    def get_state_copy(self, state_type="raw"):
        if state_type == "raw":
            return deepcopy(self.current_state)
        elif state_type == None:
            return None
