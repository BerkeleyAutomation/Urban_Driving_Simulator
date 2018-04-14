import json
import gym
import gym_urbandriving as uds
from gym_urbandriving import *
from gym_urbandriving.agents import *
from gym_urbandriving.assets import *
from gym_urbandriving.utils import Trajectory
import numpy as np
import IPython
from gym_urbandriving.actions import VelocityAction

with open('configs/default_config.json') as json_data_file:
    data = json.load(json_data_file)


data['agents']['action_space'] = 'velocity'
action = [VelocityAction(0.0)]

env = uds.UrbanDrivingEnv(data)

obs,reward,done,info_dict = env.step(action)

assert(env.current_state.dynamic_objects['controlled_cars']['0'].vel == 0.0)


