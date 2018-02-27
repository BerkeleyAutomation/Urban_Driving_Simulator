import gym
import gym_urbandriving as uds
import cProfile
import time
import numpy as np
import math
import random

from gym_urbandriving.agents import KeyboardAgent, AccelAgent, NullAgent, TrafficLightAgent, PursuitAgent, ControlAgent
from gym_urbandriving.planning import Trajectory, CasteljauPlanner
from gym_urbandriving.assets import Car, TrafficLight

from copy import deepcopy

"""
 Test File, to demonstrate general functionality of environment
"""

NUM_CARS = 4

def position_function(res_path, num_points, v0, v1, timestep):
    if abs(v0-v1<.0001):
        dist = v0*timestep
    else:
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


    agents = []

    for i in range(NUM_CARS):
        agents.append(PursuitAgent(i))
    for i in range(NUM_CARS, NUM_CARS+4):
        agents.append(TrafficLightAgent(i))

    sim_time = 0
    
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
    for sim_time in range(400):
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

        for x in range(NUM_CARS):
            state_copy = deepcopy(state)
            testing_env = uds.UrbanDrivingEnv(init_state=state_copy,
                                      visualizer=None,
                                      max_time=500,
                                      randomize=False,
                                      agent_mappings={Car:NullAgent,
                                                      TrafficLight:TrafficLightAgent},
                                      use_ray=False
            )
            state_copy = testing_env.current_state
            if state_copy.dynamic_objects[x].trajectory.stopped:
                state_copy.dynamic_objects[x].trajectory.restart()
                for t in range(10): 
                    actions = []
                    for agent in agents:
                        action = agent.eval_policy(state_copy)
                        actions.append(action)
                    state_copy, reward, done, info_dict = testing_env._step_test(actions)
                    done = state_copy.collides_any(x)
                    if done:
                        break
                if not done:
                    state.dynamic_objects[x].trajectory.restart()

            elif not state_copy.dynamic_objects[x].trajectory.stopped:
                #state_copy.dynamic_objects[x].trajectory.modify_to_stop()
                for t in range(10): 
                    actions = []
                    for agent in agents:
                        action = agent.eval_policy(state_copy)
                        actions.append(action)
                    state_copy, reward, done, info_dict = testing_env._step_test(actions)
                    done = state_copy.collides_any(x)
                    if done:
                        break
                if done:
                    state.dynamic_objects[x].trajectory.modify_to_stop()
    
        actions = []
        for agent in agents:
            action = agent.eval_policy(state)
            actions.append(action)
        for i in range(NUM_CARS):
            action_trajs[i].add_point(actions[i])
        state, reward, done, info_dict = env._step_test(actions)
        #print actions[:NUM_CARS]
        #print [obj.vel for obj in state.dynamic_objects[:NUM_CARS]]
        env._render()
        print sim_time

        #for index in range(NUM_CARS):
            #obj = state.dynamic_objects[index]
            #print "actual", obj.x, obj.y
            #print "predicted", position_function(pos_functions_args[index][0], pos_functions_args[index][1], pos_functions_args[index][2], pos_functions_args[index][3], sim_time - pos_functions_args[index][4])

        
    state = visualizing_env.current_state
    
    agents = []
    for i in range(NUM_CARS):
        agents.append(ControlAgent(i))
        obj = state.dynamic_objects[i]
        obj.trajectory = action_trajs[i]
    for i in range(NUM_CARS, NUM_CARS+4):
        agents.append(TrafficLightAgent(i))


    for sim_time in range(400):
        actions = []
        for agent in agents:
            action = agent.eval_policy(state)
            actions.append(action)
        
        state, reward, done, info_dict = visualizing_env._step_test(actions)
        visualizing_env._render()

# Collect profiling data
#cProfile.run('f()', 'temp/stats')
while (True):
    f()

