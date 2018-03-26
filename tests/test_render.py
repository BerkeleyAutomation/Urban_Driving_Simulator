import json
import gym
import gym_urbandriving as uds
from gym_urbandriving import *
from gym_urbandriving.agents import *
from gym_urbandriving.assets import *
from gym_urbandriving.planning import Trajectory
import numpy as np
import IPython

with open('configs/default_config.json') as json_data_file:
    data = json.load(json_data_file)

print data

env = uds.UrbanDrivingEnv(data,visualizer = True)


env._render()




