import gym
import gym_urbandriving as uds
import cProfile
import time
import numpy as np

from gym_urbandriving.agents import KeyboardAgent, AccelAgent, NullAgent, TrafficLightAgent, RRTAgent
from gym_urbandriving.assets import Car, TrafficLight


"""
 Test File, to demonstrate general functionality of environment
"""


def f():
    # Instantiate a PyGame Visualizer of size 800x800
    vis = uds.PyGameVisualizer((800, 800))

    # Create a simple-intersection state, with 4 cars, no pedestrians, and traffic lights
    init_state = uds.state.SimpleIntersectionState(ncars=2, nped=0, traffic_lights=True)

    # Create the world environment initialized to the starting state
    # Specify the max time the environment will run to 500
    # Randomize the environment when env._reset() is called
    # Specify what types of agents will control cars and traffic lights
    # Use ray for multiagent parallelism
    env = uds.UrbanDrivingEnv(init_state=init_state,
                              visualizer=vis,
                              max_time=500,
                              randomize=True,
                              agent_mappings={Car:NullAgent,
                                              TrafficLight:TrafficLightAgent},
                              use_ray=False
    )

    env._render()
    state = env.get_state_copy()

    # Car 0 will be controlled by our KeyboardAgent
    agent = RRTAgent()
    #agent_two = RRTAgent(agent_num=1)
    action = None

    # Simulation loop
    while(True):
        # Determine an action based on the current state.
        # For KeyboardAgent, this just gets keypresses
        start_time = time.time()
        action = agent.eval_policy(state)
        state, reward, done, info_dict = env._step(action)

        #action_two = agent_two.eval_policy(state)
        #state, reward, done, info_dict = env._step(action_two)
        

        # Simulate the state
       
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
