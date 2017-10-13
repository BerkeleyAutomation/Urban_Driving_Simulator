import gym
import gym_urbandriving as uds
import cProfile
import time

from gym_urbandriving.agents import KeyboardAgent, SimpleAvoidanceAgent, AccelAgent, NullAgent

import numpy as np


def f():

    vis = uds.PyGameVisualizer((800, 800))
    init_state = uds.state.ArenaState(ncars=5, nped=0)

    env = uds.UrbanDrivingEnv(init_state=init_state,
                              visualizer=vis,
                              bgagent=AccelAgent,
                              max_time=250,
                              randomize=True,
                              nthreads=4)
    env._render()
    state = init_state
    agent = AccelAgent()
    action = None
    while(True):
        action = agent.eval_policy(state)

        start_time = time.time()
        state, reward, done, info_dict = env._step(action)
        env._render()
        if done:
            print("done")
            time.sleep(1)
            print(info_dict["dynamic_collisions"])
            env._reset()

cProfile.run('f()', 'stats')
