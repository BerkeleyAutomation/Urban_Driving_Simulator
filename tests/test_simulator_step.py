import json
import gym
import gym_urbandriving as uds
from gym_urbandriving import *
from gym_urbandriving.agents import *
from gym_urbandriving.assets import *
from gym_urbandriving.utils import Trajectory
import numpy as np
import IPython
from gym_urbandriving.actions import SteeringAction

with open('configs/default_config.json') as json_data_file:
    data = json.load(json_data_file)

action = [SteeringAction(0.0,0.0)]
env = uds.UrbanDrivingEnv(data)

observations,reward,done,info_dict = env.step(action)
state = env.current_state

assert(state.dynamic_objects['controlled_cars']['0'].vel == 0.0)


