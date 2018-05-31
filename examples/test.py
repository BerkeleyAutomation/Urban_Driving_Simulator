import gym
import gym_urbandriving as uds
import numpy as np

import json
from gym_urbandriving.agents import KeyboardAgent, VelocitySupervisor, SteeringSupervisor
from gym_urbandriving.actions import SteeringAction

"""
 Test File, to demonstrate general functionality of environment
"""


config = json.load(open('configs/example_config.json'))
config['environment']['visualize'] = True
# config['agents']["number_of_pedestrians"] = 4
# config['agents']['agent_mappings']['Car'] = 'NeuralPursuitAgent'
# config['agents']['state_space'] = 'raw'
# config['agents']['action_space'] = 'velocity'
env = uds.UrbanDrivingEnv(config_data=config)
    
env._reset()
env._render()
obs = env.get_initial_observations()

# Car 0 will be controlled by our KeyboardAgent
agent = KeyboardAgent()
# agent = SteeringSupervisor()
# agent = VelocitySupervisor()

# Simulation loop
while(True):
    # Determine an action based on the current state.
    # For KeyboardAgent, this just gets keypresses
    action = agent.eval_policy(obs[0])

    
    # Simulate the state
    obs, reward, done, info_dict = env._step([action])
    env._render()

    if done:
        print("done")

        env._reset()
        obs = env.get_initial_observations()
