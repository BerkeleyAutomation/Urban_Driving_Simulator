import gym
import gym_urbandriving as uds
from gym_urbandriving import *
from gym_urbandriving.agents import *
from gym_urbandriving.assets import *
import numpy as np

"""
Test if an Accel Agent will move forward into an intersection but stop before colliding into an non-moving obstacle. 
"""

init_state = uds.state.SimpleIntersectionState(ncars=2, nped=0, traffic_lights=False, car_model="kinematic")
init_state.dynamic_objects[1].x = 500
init_state.dynamic_objects[1].y = 500
init_state.dynamic_objects[1].angle = 0
init_state.dynamic_objects[1].vel = 0

init_state.dynamic_objects[0].x = 450
init_state.dynamic_objects[0].y = 200
init_state.dynamic_objects[0].angle = -np.pi/2
init_state.dynamic_objects[0].vel = 0
env =  uds.UrbanDrivingEnv(init_state=init_state,
                              randomize=False,
                              agent_mappings={Car:NullAgent,
                                            },
                              use_ray=False, 
    )

agent = AccelAgent()
action = None
state = env.current_state

# Simulation loop
t = 0
while(t < 100):
    # Determine an action based on the current state.
    # For KeyboardAgent, this just gets keypresses
    action = agent.eval_policy(state)

    # Simulate the state
    state, reward, done, info_dict = env._step(action)
    env._render()
    # keep simulator running in spite of collisions or timing out

    # If we crash, sleep for a moment, then reset
    if done:
        assert False
        exit(1)
    t += 1


# We have hit 100 timesteps, should be fine. 
assert env.current_state.dynamic_objects[0].y > 300