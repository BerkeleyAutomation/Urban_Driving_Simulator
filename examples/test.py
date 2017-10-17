import gym
import gym_urbandriving as uds
import cProfile
import time

from gym_urbandriving.agents import KeyboardAgent, AccelAgent, NullAgent

import numpy as np
import ray

def f():
    ray.init()
    vis = uds.PyGameVisualizer((800, 800))
    init_state = uds.state.SimpleIntersectionState(ncars=1, nped=0)
    env = uds.UrbanDrivingEnv(init_state=init_state,
                              visualizer=vis,
                              max_time=250,
                              randomize=True,
                              bgagent=AccelAgent,
    )
    env._render()
    state = init_state
    #agent = AccelAgent.remote()
    agent = KeyboardAgent()
    action = None
    while(True):
        #actionid = agent.eval_policy.remote(state)
        #action = ray.get(actionid)
        action = agent.eval_policy(state)
        start_time = time.time()
        state, reward, done, info_dict = env._step(action)
        env._render()
        print(1/(time.time() - start_time))
        if done:
            print("done")
            time.sleep(1)
            print(info_dict["dynamic_collisions"])
            env._reset()

cProfile.run('f()', 'temp/stats')
