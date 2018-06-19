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


data['agents']['action_space'] = "velocity"
data['agents']['state_space'] = 'raw'
data['agents']['controlled_cars'] = 1
data['agents']['background_cars'] = 3

data['environment']['visualize'] = False
sup = VelocitySupervisor(agent_num = 0)


env = uds.UrbanDrivingEnv(data)
state = env.current_state

for i in range(3):
    action = sup.eval_policy(state)
    obs,reward,done,info_dict = env.step([action])
    state = obs[0]



sup = SteeringSupervisor(agent_num = 0)
data['agents']['action_space'] = "steering"
env = uds.UrbanDrivingEnv(data)
state = env.current_state

for i in range(3): 
    action = sup.eval_policy(state)
    obs,reward,done,info_dict = env.step([action])
    state = obs[0]

