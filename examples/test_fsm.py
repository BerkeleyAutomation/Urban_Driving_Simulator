import gym
import gym_urbandriving as uds
import cProfile
import time
import numpy as np
import math
import random

from gym_urbandriving.agents import KeyboardAgent, AccelAgent, NullAgent, TrafficLightAgent, PursuitAgent, ControlAgent, PlanningPursuitAgent
from gym_urbandriving.planning import Trajectory, CasteljauPlanner, GeometricPlanner, VelocityMPCPlanner

from gym_urbandriving.assets import Car, TrafficLight

from copy import deepcopy

"""
 Test File, to demonstrate general functionality of environment
"""

NUM_CARS = 4
NUM_PEDS = 0
NUM_LIGHTS = 4
DEMO_LEN = 30


def f():
    # Instantiate a PyGame Visualizer of size 800x800
    vis = uds.PyGameVisualizer((800, 800))

    # Create a simple-intersection state, with 4 cars, no pedestrians, and traffic lights
    init_state = uds.state.SimpleIntersectionState(ncars=NUM_CARS, nped=0, traffic_lights=True)


    # Create the world environment initialized to the starting state
    # Specify the max time the environment will run to 500
    # Randomize the environment when env._reset() is called
    # Specify what types of agents will control cars and traffic lights
    # Use ray for multiagent parallelism
    visualizing_env = uds.UrbanDrivingEnv(init_state=init_state,
                              visualizer=vis,
                              max_time=500,
                              randomize=False,
                              agent_mappings={Car:ControlAgent,
                                              TrafficLight:TrafficLightAgent},
                              use_ray=False
    )

    visualizing_env._reset()
    state = visualizing_env.current_state



    geoplanner = GeometricPlanner(deepcopy(state), inter_point_d=40.0, planning_time=0.1, num_cars = NUM_CARS)

    geo_trajs = geoplanner.plan_all_agents(state)
        

    sim_time = 0

    action_trajs = [Trajectory(mode = 'cs') for _ in range(NUM_CARS)]

    #max_e = 0
    # Simulation loop
    env = uds.UrbanDrivingEnv(init_state=deepcopy(state),
                              visualizer=vis,
                              max_time=500,
                              randomize=False,
                              agent_mappings={Car:NullAgent,
                                              TrafficLight:TrafficLightAgent},
                              use_ray=False
    )


    env._reset()
    state = env.current_state


    action_trajs = [Trajectory(mode = 'cs') for _ in range(NUM_CARS)]   


    agents = []
    for i in range(0, NUM_CARS+NUM_PEDS): # TODO FIX FOR PEDS
        agents.append(PursuitAgent(i))
    for i in range(NUM_CARS + NUM_PEDS, NUM_CARS + NUM_PEDS + NUM_LIGHTS):
        agents.append(TrafficLightAgent(i))


    for sim_time in range(DEMO_LEN):
        actions = [] 

        for agent_num in range(NUM_CARS+NUM_PEDS):
            target_vel = VelocityMPCPlanner().plan(deepcopy(state), agent_num)
            state.dynamic_objects[agent_num].trajectory.set_vel(target_vel)

        for agent in agents:
            actions.append(agent.eval_policy(state))
        # Simulate the state
        state, reward, done, info_dict = env._step_test(actions)
        env._render()
        for i in range(NUM_CARS):
            action_trajs[i].add_point(info_dict['saved_actions'][i])


    state = visualizing_env.current_state
    agent = ControlAgent(0)

    agents = []
    for i in range(NUM_CARS):
        agents.append(ControlAgent(i))
        obj = state.dynamic_objects[i]
        obj.trajectory = action_trajs[i]
    for i in range(NUM_CARS, NUM_CARS+4):
        agents.append(TrafficLightAgent(i))



    for sim_time in range(DEMO_LEN):
        action = agent.eval_policy(state)
        # Simulate the state
        state, reward, done, info_dict = visualizing_env._step(action)
        visualizing_env._render()

# Collect profiling data
#cProfile.run('f()', 'temp/stats')
while (True):
    f()
