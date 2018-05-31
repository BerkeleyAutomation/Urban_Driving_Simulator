import json
import gym
import gym_urbandriving as uds
from gym_urbandriving import *
from gym_urbandriving.agents import *
from gym_urbandriving.assets import *
from gym_urbandriving.utils import Trajectory
from gym_urbandriving.actions import SteeringAction
import numpy as np
import IPython

with open('configs/default_config.json') as json_data_file:
    data = json.load(json_data_file)
data['agents']['controlled_cars'] = 2
data['environment']['visualize'] = True
data['agents']['state_space'] = 'bmp'

action = [SteeringAction(0, 0)] * 2
env = uds.UrbanDrivingEnv(data)

observations,reward,done,info_dict = env.step(action)
assert(len(observations) == 2)
import matplotlib.pyplot as plt
plt.imshow(observations[0])
plt.show()
state = env.current_state

assert(state.dynamic_objects['controlled_cars']['0'].vel == 0.0)


