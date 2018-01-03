import gym
import gym_urbandriving as uds
import cProfile
import time
import numpy as np
import IPython
import numpy.linalg as LA

from gym_urbandriving.agents import KeyboardAgent, AccelAgent, NullAgent, TrafficLightAgent, RRTMAgent, RRTMPlanner
from gym_urbandriving.assets import Car, TrafficLight

NUM_CARS = 3
NUM_DATA_POINTS = 15
THRESH = 70
PLANNERS = ['EST','KPIECE','SST','RRT']
TIME = [30.0,60.0,120.0,300.0]

#UNCOMMENT FOR DEBUG
# PLANNERS = ['RRT']
# TIME = [1.0]



"""
 Test File, to demonstrate general functionality of environment
"""

def check_success(rollouts):

    goal_states = rollouts[0]
    final_states = rollouts[-1]['state'].dynamic_objects

    for i in range(NUM_CARS):
        goal_state = np.array([goal_states[i][0],goal_states[i][1]])
        car_state = np.array([final_states[i].x,final_states[i].y])

        norm = LA.norm(goal_state - car_state)


        if norm > THRESH:
            return False

    return True



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

    lane_count = 0
    while True:
        lane = lane_orders[lane_count]

        #append current lane to constraint set
        forbidden_lanes.append(lane)
        count = 0 
        while True:
            random_lane = np.random.random_integers(0, 3)
            
            if not random_lane in forbidden_lanes:
                #remove current lane from constraint set
                forbidden_lanes.pop()
                #add the assigned lane
                forbidden_lanes.append(random_lane)
                sorted_goal.append(goal_states[random_lane])
                lane_count += 1
                break;

            if len(forbidden_lanes) == 4:
                forbidden_lanes = []
                sorted_goal = []
                lane_count = 0
                break;
        
        if lane_count == NUM_CARS:
            break;


    return sorted_goal




def f(planner,time):

    rollout = []
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
    rollout.append(goal_states)
    #NSEW 

    for i in range(NUM_CARS):

        agents.append(RRTMAgent(goal_states[i],agent_num = i))
    
    

    # Car 0 will be controlled by our KeyboardAgent
    planner = RRTMPlanner(agents,planner = planner,time = time)
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
        
        i = 0 

        actions = []
        for agent in agents:
            action = agent.eval_policy(state)
            actions.append(action)

        sar = {}

        state, reward, done, info_dict = env._step_test(actions)

        sar['state'] = state
        sar['reward'] = reward
        sar['action'] = actions

        rollout.append(sar)

        # Simulate the state
       
        env._render()
        # keep simulator running in spite of collisions or timing out
        done = False
        # If we crash, sleep for a moment, then reset
        if agents[0].is_done():
            return rollout

    


def collect_data():
    rollouts = []

    stats = []

    for planner in PLANNERS:
        for time in TIME:
            data_point = {}

            data_point['time'] = time
            data_point['planner'] = planner

            success_rate = 0.0


            for i in range(NUM_DATA_POINTS):

                rollout = f(planner,time)
                if check_success(rollout):
                    success_rate += 1.0

            data_point['success_rate'] = success_rate/float(NUM_DATA_POINTS)
            stats.append(data_point)


    print stats





# Collect profiling data
collect_data()

