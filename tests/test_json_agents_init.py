import json
import gym
import gym_urbandriving as uds
from gym_urbandriving import *
from gym_urbandriving.agents import *
from gym_urbandriving.assets import *
from gym_urbandriving.utils import Trajectory
import numpy as np

with open('configs/default_config.json') as json_data_file:
    data = json.load(json_data_file)

state = uds.state.PositionState(data)


assert(len(state.dynamic_objects['controlled_cars']) == 1)
assert(len(state.dynamic_objects['background_cars']) == 3)
assert(len(state.dynamic_objects['traffic_lights']) == 4)
