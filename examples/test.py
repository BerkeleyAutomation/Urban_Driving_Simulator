import gym
import gym_urbandriving as uds
import cProfile
import time

from gym_urbandriving.agents import KeyboardAgent, AccelAgent, NullAgent

import numpy as np

def f():
    vis = uds.PyGameVisualizer((800, 800))
    init_state = uds.state.SimpleIntersectionState(ncars=4, nped=2)
    env = uds.UrbanDrivingEnv(init_state=init_state,
                              visualizer=vis,
                              max_time=250,
                              randomize=True,
                              bgagent=NullAgent,
                              use_ray=True
    )
    env._render()
    state = init_state
    agent = KeyboardAgent()
    action = None
    while(True):
        action = agent.eval_policy(state)
        start_time = time.time()
        state, reward, done, info_dict = env._step(action)
        env._render()
        print(state.min_dist_to_coll(0))
        done = False
        if done:
            print("done")
            time.sleep(1)
            print(info_dict["dynamic_collisions"])
            env._reset()
            state = env.current_state


cProfile.run('f()', 'temp/stats')
