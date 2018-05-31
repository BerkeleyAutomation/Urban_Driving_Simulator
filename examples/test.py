import gym
import gym_urbandriving as uds
import numpy as np

import json
from gym_urbandriving.agents import KeyboardAgent
from gym_urbandriving.actions import SteeringAction

"""
 Test File, to demonstrate general functionality of environment
"""


config = json.load(open('configs/default_config.json'))
config['environment']['visualize'] = True
env = uds.UrbanDrivingEnv(config_data=config)
    
env._reset()
env._render()
obs = env.get_initial_observations()

# Car 0 will be controlled by our KeyboardAgent
agent = KeyboardAgent()
action = SteeringAction(0, 0)

# Simulation loop
while(True):
    # Determine an action based on the current state.
    # For KeyboardAgent, this just gets keypresses
    action = agent.eval_policy(obs[0])

    
    # Simulate the state
    obs, reward, done, info_dict = env._step([action, action])
    env._render()
    # keep simulator running in spite of collisions or timing out
    done = False
    # If we crash, sleep for a moment, then reset
    if done:
        print("done")

        env._reset()
        obs = env.get_initial_observations()
