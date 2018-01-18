import gym
import gym_urbandriving as uds
import cProfile
import time
import numpy as np
import numpy.linalg as LA
import IPython

from gym_urbandriving.agents import KeyboardAgent, AccelAgent, NullAgent, TrafficLightAgent, RRTMAgent, RRTMPlanner
from gym_urbandriving.assets import Car, TrafficLight
from gym_urbandriving.utils.data_logger import DataLogger
from gym_urbandriving.learner.imitation_learner import IL

NUM_CARS = 2
NUM_DATA_POINTS = 1

PLANNERS = ['SST']
TIME = [1.0]

GOAL_BIAS = [0.05]
PRUNE_RADIUS = [0.5]
SELECTION_RADIUS = [0.2]

THRESH = 150



il_learn = IL('test_data')


class Trainer:

    def __init__(self,file_path,time = 3.0, goal_bias = 0.05, planner = 'SST',num_data_points = 10, num_eval_points = 10, time_horizon = 2):

        self.PLANNERS = planner
        self.TIME = time

        self.GOAL_BIAS = goal_bias
        self.PRUNE_RADIUS = 0.5
        self.SELECTION_RADIUS = 0.2
        self.NUM_DATA_POINTS = num_data_points
        self.NUM_EVAL_POINTS = num_eval_points

        self.d_logger = DataLogger(file_path)
        self.il_learn = IL(file_path)
        self.time_horizon = time_horizon

    def check_success(self,rollouts,g_state):

        
        final_states = rollouts[-1]['state'].dynamic_objects

        for i in range(NUM_CARS):
           
            goal_state = np.array([g_state[i][0],g_state[i][1]])
            car_state = np.array([final_states[i].x,final_states[i].y])

            norm = LA.norm(goal_state - car_state)


            if norm > THRESH:
                return False

        return True



    def assign_goal_state(self,lane_orders):

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
        lane_pick = []

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
                    lane_pick.append(random_lane)
                    lane_count += 1

                    break;

                if len(forbidden_lanes) == 4:
                    forbidden_lanes = []
                    sorted_goal = []
                    lane_pick = []
                    lane_count = 0
                    break;
            
            if lane_count == NUM_CARS:
                break;


        return sorted_goal, lane_pick


    def train_model(self):

        self.il_learn.load_data()
        self.il_learn.train_model()


    def get_stats(self):

        stats = {}
        stats['train_sup'] = self.il_learn.get_train_error()
        stats['loss_sup']  = self.il_learn.get_test_error()
        stats['reward_sup'] = self.success_rate

        loss_robot,success_rate = self.evaluate_policy()
        stats['loss_robot'] = loss_robot
        stats['reward_robot'] = success_rate

        return stats



    def evaluate_policy(self):

        evaluations,success_rate = self.collect_policy_rollouts()

        loss_robot = self.il_learn.get_cs(evaluations)

        return loss_robot,success_rate


    def initialize_world(self):
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

        return env

    def rollout_supervisor(self):

        rollout = []
        agents = []

        env = self.initialize_world()
        
        state = env.get_state_copy()

        goal_states, lane_pick = self.assign_goal_state(env.init_state.lane_order)
        
        self.d_logger.log_info('lane_order',env.init_state.lane_order)
        self.d_logger.log_info('lane_pick',env.init_state.lane_order)
        self.d_logger.log_info('goal_states',goal_states)
        

        for i in range(NUM_CARS):

            agents.append(RRTMAgent(goal_states[i],agent_num = i))
    
        planner = RRTMPlanner(agents,planner = self.PLANNERS,time = self.TIME, goal = self.GOAL_BIAS,prune = self.PRUNE_RADIUS,selection = self.SELECTION_RADIUS)
        plans  = planner.plan(state)
       
        for i  in range(len(plans)):
            agent = agents[i]
            plan = plans[i]
            agent.add_plan(plan)


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
           
            # If we crash, sleep for a moment, then reset
            if agents[0].is_done():
                return rollout,goal_states


    def rollout_policy(self):

        rollout = []
        agents = []

        env = self.initialize_world()
        
        state = env.get_state_copy()

        goal_states, lane_pick = self.assign_goal_state(env.init_state.lane_order)
        
        
        for i in range(NUM_CARS):
            agents.append(RRTMAgent(goal_states[i],agent_num = i))
    
        planner = RRTMPlanner(agents,planner = self.PLANNERS,time = self.TIME, goal = self.GOAL_BIAS,prune = self.PRUNE_RADIUS,selection = self.SELECTION_RADIUS)
        plans  = planner.plan(state)
       
        # Simulation loop
        for i in range(self.time_horizon):
            # Determine an action based on the current state.
            # For KeyboardAgent, this just gets keypresses
            
            i = 0 

            actions = self.il_learn.eval_model(state,goal_states)
            state = env.get_state_copy()
       
            plans  = planner.plan(state)

            if plans == None: 
                return rollout,goal_states


            sup_actions = []
            for i in range(len(agents)):
                sup_actions.append(plans[i][0])


            sar = {}

            state, reward, done, info_dict = env._step_test(actions)

            sar['state'] = state
            sar['reward'] = reward
            sar['action'] = actions
            sar['sup_action'] = sup_actions

            rollout.append(sar)
           
            env._render()

        return rollout,goal_states


    def collect_policy_rollouts(self):
        policy_success_rate = 0.0
        evaluations = []
        for i in range(self.NUM_EVAL_POINTS):

            rollout,g_s = self.rollout_policy()
            if self.check_success(rollout,g_s):
                success_rate += 1.0
            evaluations.append(rollout)
            
      
        policy_success_rate = policy_success_rate/float(NUM_DATA_POINTS)

        return evaluations, policy_success_rate

    def collect_supervisor_rollouts(self):
        success_rate = 0.0

        for i in range(NUM_DATA_POINTS):

            rollout,g_s = self.rollout_supervisor()
            if self.check_success(rollout,g_s):
                success_rate += 1.0
            
            self.d_logger.log_info('success', self.check_success(rollout,g_s))
            self.d_logger.save_rollout(rollout)

      
        self.success_rate = success_rate/float(NUM_DATA_POINTS)


