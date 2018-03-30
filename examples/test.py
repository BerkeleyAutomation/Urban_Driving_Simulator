import gym
import gym_urbandriving as uds
import cProfile
import time
import numpy as np

import json
from gym_urbandriving.agents import KeyboardAgent

"""
 Test File, to demonstrate general functionality of environment
"""


def f():
    config = json.load(open('configs/default_config.json'))
    config['environment']['visualize'] = True
    config['agents']['background_cars'] = 3
    env = uds.UrbanDrivingEnv(config_data=config)
    
    env._reset()
    env._render()
    state = env.current_state

    # Car 0 will be controlled by our KeyboardAgent
    agent = KeyboardAgent()
    action = None

    # Simulation loop
    while(True):
        # Determine an action based on the current state.
        # For KeyboardAgent, this just gets keypresses
        action = agent.eval_policy(state)
        start_time = time.time()

        # Simulate the state
        state, reward, done, info_dict = env._step([action])
        env._render()
        # keep simulator running in spite of collisions or timing out
        done = False
        # If we crash, sleep for a moment, then reset
        if done:
            print("done")
            time.sleep(1)
            env._reset()
            state = env.current_state

# Collect profiling data
cProfile.run('f()', 'temp/stats')
