import gym
import gym_urbandriving as uds
from gym_urbandriving import *
from gym_urbandriving.agents import *
from gym_urbandriving.assets import *
import numpy as np
import json

config = json.load(open('configs/default_config.json'))
config['agents']['background_cars'] = 0
env = uds.UrbanDrivingEnv(config_data=config)
state = env.current_state
state.dynamic_objects['controlled_cars']['0'].x = 100
state.dynamic_objects['controlled_cars']['0'].y = 550
state.dynamic_objects['controlled_cars']['0'].angle = 0
state.dynamic_objects['controlled_cars']['0'].vel = 0

for i in range(80):
    state, reward, done, info_dict = env._step([(0, 1)])
    car = state.dynamic_objects['controlled_cars']['0']
    #print(car.x, car.y, car.angle, done)
    assert not done

for i in range(23):
    state, reward, done, info_dict = env._step([(1, 1)])
    car = state.dynamic_objects['controlled_cars']['0']
    #print(car.x, car.y, car.angle, done)
    assert not done

for i in range(70):
    state, reward, done, info_dict = env._step([(0, 1)])
    car = state.dynamic_objects['controlled_cars']['0']
    assert not done
