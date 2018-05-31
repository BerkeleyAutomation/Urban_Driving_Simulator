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
  data['agents']['background_cars'] = 0
  data['environment']['visualize'] = False
  env = uds.UrbanDrivingEnv(data)

  state = env.current_state

  state.dynamic_objects['controlled_cars']['0'].x = 100
  state.dynamic_objects['controlled_cars']['0'].y = 550
  state.dynamic_objects['controlled_cars']['0'].angle = 0
  state.dynamic_objects['controlled_cars']['0'].vel = 0

  for i in range(80):
    action = [SteeringAction(0.0,1.0)]
    observations,reward,done,info_dict = env.step(action)
    assert(not done)
  for i in range(23):
    action = [SteeringAction(1.0,1.0)]
    observations,reward,done,info_dict = env.step(action)
    assert(not done)
  for i in range(70):
    action = [SteeringAction(0.0,1.0)]
    observations,reward,done,info_dict = env.step(action)
    assert(not done)


  assert(state.dynamic_objects['controlled_cars']['0'].x < 528 and state.dynamic_objects['controlled_cars']['0'].x > 527)
  assert(state.dynamic_objects['controlled_cars']['0'].y < 110 and state.dynamic_objects['controlled_cars']['0'].y > 109)
