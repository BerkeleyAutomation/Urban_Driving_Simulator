import gym
import gym_urbandriving as uds
import cProfile
import time
import numpy as np

from gym_urbandriving.agents import KeyboardAgent, AccelAgent, NullAgent


def f():

    # Initialize Pygame visualizer, State, and UrbanDrivingEnv
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
        # keep simulator running in spite of collisions or timing out
        done = False
        if done:
            print("done")
            time.sleep(1)
            env._reset()
            state = env.current_state


cProfile.run('f()', 'temp/stats')
