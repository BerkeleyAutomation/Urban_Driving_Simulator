import gym
import gym_urbandriving as uds
import cProfile
import time
import numpy as np

from gym_urbandriving.agents import NullAgent, TrafficLightAgent, ControlAgent
from gym_urbandriving.planning import RRTMAgent, RRTMPlanner
from gym_urbandriving.assets import Car, TrafficLight

NUM_CARS = 2

"""
 Test File, to demonstrate general functionality of environment
"""

def f():
    # Instantiate a PyGame Visualizer of size 800x800
    vis = uds.PyGameVisualizer((800, 800))

    # Create a simple-intersection state, with cars, no pedestrians, and traffic lights
    init_state = uds.state.SimpleIntersectionState(ncars=NUM_CARS, nped=0, traffic_lights=True)

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

    state = env.current_state
    agents = []

    for c in state.dynamic_objects[:NUM_CARS]:
        print '[',c.x, c.y, c.vel, c.angle, ']', c.destination

    for i in range(NUM_CARS):
        agents.append(ControlAgent(i))

    # Car 0 will be controlled by our KeyboardAgent
    planner = RRTMPlanner(agents, planner='SST')
    plans  = planner.plan(state)
    #plans.reverse()

    for i  in range(len(plans)):
        agent = agents[i]
        plan = plans[i]
        agent.add_plan(plan)



    #agent_two = RRTAgent(agent_num=1)
    action = None

    # Simulation loop
    while(True):
        # Determine an action based on the current state.
        # For KeyboardAgent, this just gets keypresses
        start_time = time.time()
        i = 0 

        actions = []
        for agent in agents:
            action = agent.eval_policy(state)
            actions.append(action)

        state, reward, done, info_dict = env._step_test(actions)
        print "CAR X "+ str(state.dynamic_objects[0].x) + "    Y " + str(state.dynamic_objects[0].y)
           
        
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
