import gym
import gym_urbandriving as uds
import cProfile
import time
import numpy as np
import math

from gym_urbandriving.agents import KeyboardAgent, AccelAgent, NullAgent, TrafficLightAgent, PursuitAgent
from gym_urbandriving.planning import Trajectory, CasteljauPlanner
from gym_urbandriving.assets import Car, TrafficLight

from copy import deepcopy

"""
 Test File, to demonstrate general functionality of environment
"""

NUM_CARS = 4

def position_function(res_path, num_points, v0, v1, timestep):
    dist = num_points*v0*(np.e**((v1-v0)*float(timestep)/(num_points))-1)/(v1-v0)
    frac = dist%1
    index = (int)(dist)
    if index >= num_points-1:
        return [res_path[-1][0], res_path[-1][1]]
    return [res_path[index][0]*(1-frac) + res_path[index+1][0]*(frac), res_path[index][1]*(1-frac) + res_path[index+1][1]*(frac)]


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
    env = uds.UrbanDrivingEnv(init_state=init_state,
                              visualizer=vis,
                              max_time=500,
                              randomize=False,
                              agent_mappings={Car:NullAgent,
                                              TrafficLight:TrafficLightAgent},
                              use_ray=False
    )
    
    env._reset()
    state = env.current_state

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
        obj.vel = 5
        closest_point = sorted(all_targets, key = lambda p: (p[0]-obj.x)**2+(p[1]-obj.y)**2 )[0]
        traj = Trajectory(mode = 'xyv', fsm=0)

        path_to_follow = planner.plan(obj.x,obj.y, obj.vel,obj.angle, closest_point[0],closest_point[1],4,closest_point[2])

        for p in path_to_follow:
            traj.add_point(p)

        obj.trajectory = traj
        pos_functions_args.append([deepcopy(path_to_follow), len(path_to_follow), obj.vel, 4, 0])

    agents = []

    for i in range(NUM_CARS):
        agents.append(PursuitAgent(i))


    action = None
    sim_time = 0
    max_e = 0
    # Simulation loop
    while(True):
        """
        if obj.trajectory.npoints() <= 0:
            if obj.x<300:
                for p in transform(obj.x, obj.y, obj.angle, maintain):
                    traj.add_point(p)
            elif obj.x<375 and light=='red' and obj.vel>4:
                for p in transform(obj.x, obj.y, obj.angle, decc):
                    traj.add_point(p)
            elif obj.x<375 and light=='red' and obj.vel<=4:
                obj.vel = 0
                for p in transform(obj.x, obj.y, obj.angle, stop):
                    traj.add_point(p)
            elif obj.x<375 and light=='green' and obj.vel>4:
                obj.vel = 0
                for p in transform(obj.x, obj.y, obj.angle, maintain):
                    traj.add_point(p)
            elif obj.x<375 and light=='green' and obj.vel<=4:
                obj.vel = 0
                for p in transform(obj.x, obj.y, obj.angle, acc):
                    traj.add_point(p)
            elif obj.y<600:
                for p in transform(obj.x, obj.y, obj.angle, right_full):
                    traj.add_point(p)
            elif obj.y<750:
                for p in transform(obj.x, obj.y, -np.pi/2, maintain):
                    traj.add_point(p)
            elif obj.vel > 4:
                for p in transform(obj.x, obj.y, obj.angle, slow_decc):
                    traj.add_point(p)
            else:
                obj.vel = 0
                for p in transform(obj.x, obj.y, obj.angle, stop):
                    traj.add_point(p)

        """
        for index in range(NUM_CARS):
            obj = state.dynamic_objects[index]
            if obj.trajectory.is_empty():
                traj = Trajectory(mode = 'xyv', fsm=obj.trajectory.fsm+1)
                prev = sorted(all_targets, key = lambda p: (p[0]-obj.x)**2+(p[1]-obj.y)**2)[0]
                if obj.trajectory.fsm == 0:
                    target = sorted(all_targets, key = lambda p: (p[0]-obj.destination[0])**2+(p[1]-obj.destination[1])**2)[0]
                    path_to_follow = planner.plan(prev[0], prev[1], obj.vel, prev[2], target[0],target[1],4,target[2])
                    pos_args = [deepcopy(path_to_follow), len(path_to_follow), obj.vel, 4, sim_time]
                elif obj.trajectory.fsm == 1:
                    target = [obj.destination[0], obj.destination[1], obj.destination[3]]
                    path_to_follow = planner.plan(prev[0], prev[1], obj.vel, prev[2], target[0],target[1],2,target[2])
                    pos_args = [deepcopy(path_to_follow), len(path_to_follow), obj.vel, 2, sim_time]
                else:
                    obj.vel = 0

                for p in path_to_follow:
                    traj.add_point(p)

                    obj.trajectory = traj
                pos_functions_args[index] = pos_args

        actions = []
        for agent in agents:
            action = agent.eval_policy(state)
            actions.append(action)
        state, reward, done, info_dict = env._step_test(actions)

        env._render()
        # keep simulator running in spite of collisions or timing out
        done = False
        sim_time += 1

        for index in range(NUM_CARS):
            obj = state.dynamic_objects[index]
            print "actual", obj.x, obj.y
            print "predicted", position_function(pos_functions_args[index][0], pos_functions_args[index][1], pos_functions_args[index][2], pos_functions_args[index][3], sim_time - pos_functions_args[index][4])

        # If we crash, sleep for a moment, then reset
        if done:
            print("done")
            time.sleep(1)
            env._reset()
            state = env.current_state

# Collect profiling data
cProfile.run('f()', 'temp/stats')

