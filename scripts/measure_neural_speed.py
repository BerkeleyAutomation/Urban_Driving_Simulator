import json
import gym
import gym_urbandriving as uds
from gym_urbandriving import *
from gym_urbandriving.agents import *
from gym_urbandriving.assets import *
from gym_urbandriving.utils import Trajectory
import numpy as np
import time
import matplotlib
from matplotlib import pyplot as plt
matplotlib.use("TkAgg")


plt.style.use('fivethirtyeight')
with open('configs/default_config.json') as json_data_file:
    data = json.load(json_data_file)

data['environment']['visualize'] = False

data['agents']['action_space'] = "velocity"
data['agents']['action_space'] = "steering"
data['agents']['agent_mappings']['Car'] = "CSPPursuitAgent"

time_taken_neural = []


for j in range(7):
	data['agents']['background_cars'] = j
	sup = SteeringSupervisor(agent_num = 0)

	env = uds.UrbanDrivingEnv(data)
	state = env.current_state

	action = sup.eval_policy(state)

	obs,reward,done,info_dict = env.step([action])

	start = time.time()
	obs,reward,done,info_dict = env.step([action])
	stop = time.time()

	time_taken_neural.append(stop-start)


data['agents']['agent_mappings']['Car'] = "PlanningPursuitAgent"

time_taken_planner = []


# for j in range(7):
# 	data['agents']['background_cars'] = j
# 	sup = SteeringSupervisor(agent_num = 0)

# 	env = uds.UrbanDrivingEnv(data)
# 	state = env.current_state

# 	action = sup.eval_policy(state)

# 	obs,reward,done,info_dict = env.step([action])

# 	start = time.time()
# 	obs,reward,done,info_dict = env.step([action])
# 	stop = time.time()

# 	time_taken_planner.append(stop-start)


plt.plot(time_taken_neural,label = 'CSP' )
plt.plot(time_taken_planner,label = 'Planner' )
plt.legend()

plt.ylabel('Seconds/Step')
plt.xlabel('Num Cars')

plt.show()





    


