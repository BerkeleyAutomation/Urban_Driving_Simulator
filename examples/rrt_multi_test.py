import gym
import gym_urbandriving as uds
import cProfile
import time
import numpy as np


from gym_urbandriving.agents import KeyboardAgent, AccelAgent, NullAgent, TrafficLightAgent, RRTMAgent, RRTMPlanner
from gym_urbandriving.assets import Car, TrafficLight

NUM_CARS = 2

"""
 Test File, to demonstrate general functionality of environment
"""

def assign_goal_state(lane_orders):

    #No two agents can go to the same goal 
    #No goal can be on the same starting spot
    sorted_goal = []

    #Goals organized in NSEW order
    goal_states = []
    goal_states.append([550,100,2,90])
    goal_states.append([450,900,2,270])
    goal_states.append([900,550,2,0])
    goal_states.append([100,450,2,180])

    #Lanes that cannot be assigned 
    forbidden_lanes = []

    for lane in lane_orders:

        #append current lane to constraint set
        forbidden_lanes.append(lane)

        while True:
            random_lane = np.random.random_integers(0, 3)
            if random_lane not in forbidden_lanes:
                #remove current lane from constraint set
                forbidden_lanes.pop()
                #add the assigned lane
                forbidden_lanes.append(random_lane)
                break;

        sorted_goal.append(goal_states[random_lane])


    return sorted_goal




def f():
    # Instantiate a PyGame Visualizer of size 800x800
    vis = uds.PyGameVisualizer((800, 800))

    # Create a simple-intersection state, with cars, no pedestrians, and traffic lights
    init_state = uds.state.MultiIntersectionState(ncars=NUM_CARS, nped=0, traffic_lights=True)

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
    agents = []
    goal_states = assign_goal_state(init_state.lane_order)

    #NSEW 

    for i in range(NUM_CARS):

        agents.append(RRTMAgent(goal_states[i],agent_num = i))
    
    
    

    
    

    # Car 0 will be controlled by our KeyboardAgent
    planner = RRTMPlanner(agents)
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
        print "CAR X "+ str(state.dynamic_objects[0].x) + "Y " + str(state.dynamic_objects[0].y)
           
        
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
f()
cProfile.run('f()', 'temp/stats')
