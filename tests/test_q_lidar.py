import json
import gym
import gym_urbandriving as uds
from gym_urbandriving import *
from gym_urbandriving.agents import *
from gym_urbandriving.assets import *
from gym_urbandriving.utils import Trajectory
import numpy as np
from gym_urbandriving.actions import SteeringAction

with open('configs/default_config.json') as json_data_file:
    data = json.load(json_data_file)
    
data['agents']['controlled_cars'] = 2
data['environment']['visualize'] = False
action = [SteeringAction(0.0,0.0)] * 2
env = uds.UrbanDrivingEnv(data)

observations,reward,done,info_dict = env.step(action)
assert(len(observations) == 2)
assert(len(observations[0]) == len(observations[1]))
orig_len = len(observations[0])
state = env.current_state

assert(state.dynamic_objects['controlled_cars']['0'].vel == 0.0)

data['agents']['state_space_config']['goal_position'] = True
env = uds.UrbanDrivingEnv(data)
observations,reward,done,info_dict = env.step(action)
assert(len(observations) == 2)
assert(len(observations[0]) == len(observations[1]) == orig_len + 3)
