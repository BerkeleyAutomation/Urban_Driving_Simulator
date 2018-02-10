import gym
import gym_urbandriving as uds
import cProfile
import time
import numpy as np

from gym_urbandriving.agents import KeyboardAgent, NullAgent, TrafficLightAgent, PursuitAgent
from gym_urbandriving.assets import Car, TrafficLight
from gym_urbandriving.utils import Trajectory

"""
 Test File, to demonstrate general functionality of environment
"""


def f():


    # Instantiate a PyGame Visualizer of size 800x800
    vis = uds.PyGameVisualizer((800, 800))

    # Create a simple-intersection state, with 4 cars, no pedestrians, and traffic lights
    init_state = uds.state.SimpleIntersectionState(ncars=1, nped=0, traffic_lights=True)

    # Create the world environment initialized to the starting state
    # Specify the max time the environment will run to 500
    # Randomize the environment when env._reset() is called
    # Specify what types of agents will control cars and traffic lights
    # Use ray for multiagent parallelism
    env = uds.UrbanDrivingEnv(init_state=init_state,
                              visualizer=vis,
                              max_time=500,
                              randomize=True,
                              agent_mappings={Car:PursuitAgent,
                                              TrafficLight:TrafficLightAgent},
                              use_ray=False
    )
    
    env._reset()
    state = env.current_state

    traj = Trajectory()
    traj.add_point(state.dynamic_objects[0].x, state.dynamic_objects[0].y)
    while(True):
        connector = traj.last()
        sample_x, sample_y = np.random.uniform(0,1000), np.random.uniform(0,1000)
        if np.linalg.norm(connector[:2] - np.array([sample_x, sample_y])) < 20 and np.linalg.norm(connector[:2] - np.array([450,900])) < np.linalg.norm(np.array([450,900]) - np.array([sample_x, sample_y])):
            traj.add_point(sample_x, sample_y)
            print sample_x, sample_y
        if np.linalg.norm(connector[:2] - np.array([450,900])) < 20:
            break




    # Car 0 will be controlled by our KeyboardAgent
    agent = PursuitAgent()
    action = None

    state.dynamic_objects[0].trajectory = traj
    state.dynamic_objects[0].destination = (450,900)
    # Simulation loop
    while(True):
        # Determine an action based on the current state.
        # For KeyboardAgent, this just gets keypresses
        action = agent.eval_policy(state)
        start_time = time.time()

        # Simulate the state
        state, reward, done, info_dict = env._step(action)
        env._render()
        # keep simulator running in spite of collisions or timing out
        done = False
        # If we crash, sleep for a moment, then reset
        if done:
            print("done")
            time.sleep(1)
            env._reset()
            state = env.current_state

# Collect profiling data
cProfile.run('f()', 'temp/stats')
