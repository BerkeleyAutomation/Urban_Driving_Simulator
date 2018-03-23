import gym
import gym_urbandriving as uds
from gym_urbandriving import *
from gym_urbandriving.agents import *
from gym_urbandriving.assets import *
import numpy as np

init_state = uds.state.SimpleIntersectionState(ncars=1, nped=0, traffic_lights=False, car_model="kinematic")
init_state.dynamic_objects[0].x = 100
init_state.dynamic_objects[0].y = 550
init_state.dynamic_objects[0].angle = 0
init_state.dynamic_objects[0].vel = 0
env =  uds.UrbanDrivingEnv(init_state=init_state,
                              randomize=False,
                              agent_mappings={Car:NullAgent,
                                              TrafficLight:TrafficLightAgent, 
                                              CrosswalkLight:CrosswalkLightAgent},
    )

for i in range(80):
    state, reward, done, info_dict = env._step((0, 1))
    car = state.dynamic_objects[0]
    #print(car.x, car.y, car.angle, done)
    assert not done

for i in range(23):
    state, reward, done, info_dict = env._step((1, 1))
    car = state.dynamic_objects[0]
    #print(car.x, car.y, car.angle, done)
    assert not done

for i in range(70):
    state, reward, done, info_dict = env._step((0, 1))
    car = state.dynamic_objects[0]
    assert not done
