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


data['agents']['action_space'] = "velocity"
sup = VelocitySupervisor(agent_num = 0)


env = uds.UrbanDrivingEnv(data)
state = env.current_state

for i in range(10): 
	action = sup.eval_policy(state)
	state,reward,done,info_dict = env.step([action])


# sup = SteeringSupervisor(agent_num = 0)
# data['agents']['action_space'] = "steering"
# env = uds.UrbanDrivingEnv(data)
# state = env.current_state

# for i in range(3): 
# 	action = sup.eval_policy(state)
# 	state,reward,done,info_dict = env.step([action])
