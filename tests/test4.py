import gym
import gym_urbandriving as uds
from gym_urbandriving import *
from gym_urbandriving.agents import *
from gym_urbandriving.assets import *
from gym_urbandriving.planning import Trajectory
import numpy as np

"""
Same as test1 but using control agent and trajectory and tests if final position is correct. 
"""

traj = Trajectory(mode='cs')
for i in range(80):
  traj.add_point([0,1])
for i in range(23):
    traj.add_point([1, 1])
for i in range(70):
    traj.add_point([0,1])


init_state = uds.state.SimpleIntersectionState(ncars=1, nped=0, traffic_lights=False, car_model="kinematic")

init_state.dynamic_objects[0].x = 100
init_state.dynamic_objects[0].y = 550
init_state.dynamic_objects[0].angle = 0
init_state.dynamic_objects[0].vel = 0
init_state.dynamic_objects[0].trajectory = traj

env =  uds.UrbanDrivingEnv(init_state=init_state,
                              randomize=False,
                              agent_mappings={Car:NullAgent,
                                              TrafficLight:TrafficLightAgent, 
                                              CrosswalkLight:CrosswalkLightAgent},
    )



state = env.current_state
agent = ControlAgent()

for i in range(80+23+70):
    # Determine an action based on the current state.
    # For KeyboardAgent, this just gets keypresses
    action = agent.eval_policy(state)
    # Simulate the state
    state, reward, done, info_dict = env._step(action)
    # keep simulator running in spite of collisions or timing out

assert(state.dynamic_objects[0].x < 528 and state.dynamic_objects[0].x > 527)
assert(state.dynamic_objects[0].y < 110 and state.dynamic_objects[0].y > 109)
