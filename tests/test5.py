import gym
import gym_urbandriving as uds
import time
import numpy as np

from gym_urbandriving.agents import *
from gym_urbandriving.assets import *
from gym_urbandriving.utils.data_logger import DataLogger

NUM_ITERS = 1 #Number of iterations 

FILE_PATH_ALG =  "tests/"

DISTANCE_THRESHOLDS = [2,5,10,20,40]
"""
Testable equivalent of test_pursuit, but only runs on one saved trajectory and uses a fixed threshold of 5. 
Makes sure the pursuit agent still works. 
"""


def test_rollout(index, thres):
    # Instantiate a PyGame Visualizer of size 800x800
    #vis = uds.PyGameVisualizer((1000, 1000))

    # Create a simple-intersection state, with 4 cars, no pedestrians, and traffic lights
    init_state = uds.state.SimpleIntersectionState(ncars=2, nped=0)
    # Create the world environment initialized to the starting state
    # Specify the max time the environment will run to 500
    # Randomize the environment when env._reset() is called
    # Specify what types of agents will control cars and traffic lights
    # Use ray for multiagent parallelism
    env = uds.UrbanDrivingEnv(init_state=init_state,
                              visualizer=None,
                              max_time=500,
                              randomize=True,
                              agent_mappings={Car:NullAgent},
    )
    
    env._reset()
    state = env.current_state

    data_logger = DataLogger(FILE_PATH_ALG)
    loaded_rollout = data_logger.load_rollout(index)

    # Reset the agents to be at the correct initial starting configurations. 
    state.dynamic_objects[0].destination = loaded_rollout[1]['goal_states'][0]
    state.dynamic_objects[0].x = loaded_rollout[0][0]['state'].dynamic_objects[0].x
    state.dynamic_objects[0].y = loaded_rollout[0][0]['state'].dynamic_objects[0].y
    state.dynamic_objects[0].vel = loaded_rollout[0][0]['state'].dynamic_objects[0].vel
    state.dynamic_objects[0].angle = loaded_rollout[0][0]['state'].dynamic_objects[0].angle
    loaded_rollout[1]['pos_trajs'][0].pop()
    state.dynamic_objects[0].trajectory = loaded_rollout[1]['pos_trajs'][0]
    state.dynamic_objects[0].trajectory.add_interpolated_t()

    state.dynamic_objects[1].destination = loaded_rollout[1]['goal_states'][0]
    state.dynamic_objects[1].x = loaded_rollout[0][0]['state'].dynamic_objects[0].x
    state.dynamic_objects[1].y = loaded_rollout[0][0]['state'].dynamic_objects[0].y
    state.dynamic_objects[1].vel = loaded_rollout[0][0]['state'].dynamic_objects[0].vel
    state.dynamic_objects[1].angle = loaded_rollout[0][0]['state'].dynamic_objects[0].angle
    state.dynamic_objects[1].trajectory = loaded_rollout[1]['control_trajs'][0]

    agents = [PursuitAgent(0), ControlAgent(1)]
    action = None

    # Simulation loop
    t = 0
    loss = 0
    success = True
    while(True):
        # Determine an action based on the current state.
        # For KeyboardAgent, this just gets keypresses
        actions = []
        for agent in agents:
            action = agent.eval_policy(state)
            actions.append(action)
        state, reward, done, info_dict = env._step_test(actions)
        env._render()
        # keep simulator running in spite of collisions or timing out


        one_step_loss = np.sqrt((env.current_state.dynamic_objects[0].x-env.current_state.dynamic_objects[1].x)**2
                                +(env.current_state.dynamic_objects[0].y-env.current_state.dynamic_objects[1].y)**2)
                                #+(env.current_state.dynamic_objects[0].vel-env.current_state.dynamic_objects[1].vel)**2
                                #+(diff_angle)**2)
        loss += one_step_loss

        if one_step_loss > thres:
            success = False

        t += 1
        done = (t >= len(loaded_rollout[0]))
        # If we crash, sleep for a moment, then reset
        if done:
            return loss/t, success

_, s = test_rollout(0, 5) 
assert(s)
