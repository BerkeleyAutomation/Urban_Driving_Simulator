import gym
import gym_urbandriving as uds
import cProfile
import time
import numpy as np
import math
import random

from gym_urbandriving.agents import KeyboardAgent, AccelAgent, NullAgent, TrafficLightAgent, PursuitAgent, ControlAgent, PlanningPursuitAgent
from gym_urbandriving.planning import Trajectory, CasteljauPlanner
from gym_urbandriving.assets import Car, TrafficLight

from copy import deepcopy

"""
 Test File, to demonstrate general functionality of environment
"""

NUM_CARS = 4
DEMO_LEN = 300

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
                              agent_mappings={Car:NullAgent,
                                              TrafficLight:TrafficLightAgent},
                              use_ray=False
    )
    
    visualizing_env._reset()
    state = visualizing_env.current_state

    # Car 0 will be controlled by our KeyboardAgent

    """
    agent = KeyboardAgent()
    """

    pos_functions_args = [] #(res_path, num_points, v0, v1, time offset)
    planner = CasteljauPlanner()

    all_targets = [[450,375,-np.pi/2],
                   [550,375,np.pi/2], 
                   [625,450,-np.pi],
                   [625,550,0.0],
                   [450,625,-np.pi/2],
                   [550,625,np.pi/2], 
                   [375,450,-np.pi],
                   [375,550,0.0]]

    for obj in state.dynamic_objects[:NUM_CARS]:
        obj.vel = 4
        closest_point = sorted(all_targets, key = lambda p: (p[0]-obj.x)**2+(p[1]-obj.y)**2 )[0]
        mid_target = sorted(all_targets, key = lambda p: (p[0]-obj.destination[0])**2+(p[1]-obj.destination[1])**2)[0]
        traj = Trajectory(mode = 'xyv', fsm=0)

        path_to_follow = planner.plan(obj.x,obj.y, obj.vel,obj.angle, closest_point[0],closest_point[1],4,closest_point[2])
        for p in path_to_follow:
            traj.add_point(p)
        path_to_follow = planner.plan(closest_point[0],closest_point[1],4,closest_point[2], mid_target[0],mid_target[1],4,mid_target[2])
        for p in path_to_follow:
            traj.add_point(p)
        path_to_follow = planner.plan(mid_target[0],mid_target[1],4,mid_target[2], obj.destination[0],obj.destination[1],4,obj.destination[3])
        for p in path_to_follow:
            traj.add_point(p)

        obj.trajectory = traj
        obj.vel = 0
        obj.trajectory.restart()


    sim_time = 0
    action_trajs = [Trajectory(mode = 'cs') for _ in range(NUM_CARS)]

    #max_e = 0
    # Simulation loop
    env = uds.UrbanDrivingEnv(init_state=deepcopy(state),
                              visualizer=vis,
                              max_time=500,
                              randomize=False,
                              agent_mappings={Car:PlanningPursuitAgent,
                                              TrafficLight:TrafficLightAgent},
                              use_ray=False
    )
    env._reset()
    state = env.current_state

    agent = PlanningPursuitAgent(0)
    action = None

    for sim_time in range(DEMO_LEN):

        action = agent.eval_policy(state)

        # Simulate the state
        state, reward, done, info_dict = env._step(action)
        env._render()
        for i in range(NUM_CARS):
            action_trajs[i].add_point(info_dict['saved_actions'][i])

    state = visualizing_env.current_state
    
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

