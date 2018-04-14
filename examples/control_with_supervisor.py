import json
import gym
import gym_urbandriving as uds
from gym_urbandriving import *
from gym_urbandriving.agents import *
from gym_urbandriving.assets import *
from gym_urbandriving.utils import Trajectory
import numpy as np
import IPython

with open('configs/default_config.json') as json_data_file:
    data = json.load(json_data_file)


supervisors = []

supervisors.append(SteeringSupervisor(agent_num = 0))
supervisors.append(SteeringSupervisor(agent_num = 1))

actions = []

env = uds.UrbanDrivingEnv(data)
current_global_state  = env.current_state


for t in range(5): 
    for supervisor in supervisors:
		actions.append(supervisor.eval_policy(state))

    obs,reward,done,info_dict = env.step(actions)
    current_global_state = env.current_state

   	actions = []



