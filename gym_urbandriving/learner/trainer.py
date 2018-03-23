import gym
import gym_urbandriving as uds
import cProfile
import time
import numpy as np
import numpy.linalg as LA
from copy import deepcopy

from gym_urbandriving.utils.data_logger import DataLogger
from gym_urbandriving.learner.imitation_learner import IL

from gym_urbandriving.agents import NullAgent, TrafficLightAgent, ControlAgent, PursuitAgent, CrosswalkLightAgent
from gym_urbandriving.planning import Trajectory, RRTMPlanner, GeometricPlanner, VelocityMPCPlanner, CasteljauPlanner, PedestrianVelPlanner
from gym_urbandriving.assets import Car, TrafficLight, CrosswalkLight

THRESH = 280



il_learn = IL('test_data')


class Trainer:

    def __init__(self,file_path,time = 3.0, goal_bias = 0.05, planner = 'SST',num_data_points = 10, num_eval_points = 10, time_horizon = 2,max_agents = 7):

        self.PLANNERS = planner
        self.TIME = time
        self.lookahead = 20

        self.GOAL_BIAS = goal_bias
        self.PRUNE_RADIUS = 0.5
        self.SELECTION_RADIUS = 0.2
        self.NUM_DATA_POINTS = num_data_points
        self.NUM_EVAL_POINTS = num_eval_points
        self.NUM_CARS = 0
        self.NUM_PEDS = 0
        self.DEMO_LEN = 300

        self.MAX_AGENTS = max_agents

        self.d_logger = DataLogger(file_path)
        self.il_learn = IL(file_path)
        self.time_horizon = time_horizon

    def check_success(self, state):
        for obj in state.dynamic_objects:
            if type(obj) in {Car}:
                if np.linalg.norm(np.array([obj.x, obj.y]) - np.array([obj.destination[0], obj.destination[1]])) > THRESH and not obj.trajectory.is_empty():
                    return False
        return True
    

    def train_model(self):
        """
        Loads the data and trains the model
        """

        self.il_learn.load_data()
        self.il_learn.train_model()


    def get_stats(self):
        """
        Collect statistics of each iteration

        Returns
        --------
        stats: A dictonary with each measurment corresponding to some stastistic
        """

        stats = {}
        stats['train_sup'] = self.il_learn.get_train_error()
        stats['loss_sup']  = self.il_learn.get_test_error()
        stats['reward_sup'] = self.success_rate

        loss_robot,success_rate = self.evaluate_policy()
        stats['loss_robot'] = loss_robot
        stats['reward_robot'] = success_rate

        return stats



    def evaluate_policy(self):
        """
        Use to measure the learned policy's performance

        Returns
        --------
        loss_robot: float, corresponding to the surrogate loss on the robot's distributions
        success_rate: float, corresponding to the reward of the robot
        """

        evaluations,success_rate = self.collect_policy_rollouts()

        loss_robot = self.il_learn.get_cs(evaluations)

        return loss_robot,success_rate


    def inject_noise(self,target_vel):

        draw = np.random.uniform()

        if draw > 0.2:
            return target_vel
        else:
            if target_vel == 4:
                return 0
            elif target_vel == 0:
                return 4


    def initialize_world(self):
        """
        Initialize the world of the simulator 

        Returns
        --------
        env: an enviroment of the simulator
        """

        # Instantiate a PyGame Visualizer of size 800x800
        vis = uds.PyGameVisualizer((800, 800))

        # Create a simple-intersection state, with cars, no pedestrians, and traffic lights
        init_state = uds.state.SimpleIntersectionState(ncars=self.NUM_CARS, nped=self.NUM_PEDS, traffic_lights=True)

        # Create the world environment initialized to the starting state
        # Specify the max time the environment will run to 500
        # Randomize the environment when env._reset() is called
        # Specify what types of agents will control cars and traffic lights
        # Use ray for multiagent parallelism

        env = uds.UrbanDrivingEnv(init_state=init_state,
                                  visualizer=vis,
                                  max_time=self.DEMO_LEN,
                                  randomize=True,
                                  agent_mappings={Car:NullAgent,
                                                  TrafficLight:TrafficLightAgent, 
                                                  CrosswalkLight:CrosswalkLightAgent},
        )

        env._render()
        return env

    def rollout_supervisor(self):
        """
        Rollout the supervior, by generating a plan through OMPL and then executing it. 

        Returns
        --------
        Returns the rollout and the goal states
        """

        rollout = []
        agents = []

        env = self.initialize_world()
        
        state = env.current_state

        goal_states = [c.destination for c in state.dynamic_objects[:self.NUM_CARS]]
        
        self.d_logger.log_info('goal_states',goal_states)
        
        for i in range(self.NUM_CARS+self.NUM_PEDS):
            agents.append(PursuitAgent(i))
        for i in range(self.NUM_CARS+self.NUM_PEDS, self.NUM_CARS+self.NUM_PEDS+4):
            agents.append(TrafficLightAgent(i))
        for i in range(self.NUM_CARS+self.NUM_PEDS+4 , self.NUM_CARS+self.NUM_PEDS+12):
            agents.append(CrosswalkLightAgent(i))

        geoplanner = GeometricPlanner(deepcopy(state), inter_point_d=40.0, planning_time=0.1, num_cars = self.NUM_CARS)
        geo_trajs = geoplanner.plan_all_agents(state)
        for i in range(self.NUM_CARS, self.NUM_CARS+self.NUM_PEDS):
            CasteljauPlanner().plan_agent(state.dynamic_objects[i]) # used as a linear planner


        pos_trajs = [Trajectory(mode='xyva') for _ in range(self.NUM_CARS+self.NUM_PEDS)]
        action_trajs = [Trajectory(mode = 'cs') for _ in range(self.NUM_CARS+self.NUM_PEDS)]
        agent_ids = []
        for agent_num in range(self.NUM_CARS):
            agent_ids.append(agent_num) # TODO: Lets not assume the first n dynamic objects are cars


        # Simulation loop
        for sim_time in range(self.DEMO_LEN):
            # get all actions
            actions = [] 
            target_velocities = []

            for agent_num in range(self.NUM_CARS):
                target_vel = VelocityMPCPlanner().plan(deepcopy(state), agent_num)
                state.dynamic_objects[agent_num].trajectory.set_vel(target_vel)
                target_velocities.append(target_vel)

            for agent_num in range(self.NUM_CARS, self.NUM_CARS + self.NUM_PEDS):
                target_vel = PedestrianVelPlanner().plan(deepcopy(state),agent_num)
                state.dynamic_objects[agent_num].trajectory.set_vel(target_vel)
                target_velocities.append(target_vel)



            for agent in agents:
                actions.append(agent.eval_policy(state))

            # save old state
            state_copy = env.get_state_copy()

            # break if necessary

            # Simulate the state
            state, reward, done, info_dict = env._step_test(actions)
            env._render()

            # Log all information. 
            sar = {}
            sar['state'] = state_copy
            sar['reward'] = reward
            sar['action'] = actions
            sar['target_velocities'] = target_velocities

            rollout.append(sar)

            for i in range(self.NUM_CARS+self.NUM_PEDS):
                obj = state_copy.dynamic_objects[i]
                pos_trajs[i].add_point([obj.x, obj.y, obj.vel, obj.angle])
                action_trajs[i].add_point(actions[i])

            if self.check_success(state):
                break

        self.d_logger.log_info('control_trajs', action_trajs)
        self.d_logger.log_info('pos_trajs', pos_trajs)
        self.d_logger.log_info('agent_ids', agent_ids)
        return rollout,deepcopy(env.current_state)


    def rollout_policy(self):
        """
        Rolls out the policy by executing the learned behavior

        Returns
        --------
        Returns the rollout and the goal states
        """

        rollout = []
        agents = []

        env = self.initialize_world()
        
        state = env.current_state

        goal_states = [c.destination for c in state.dynamic_objects[:self.NUM_CARS]]
        
        self.d_logger.log_info('goal_states',goal_states)
        

        for i in range(self.NUM_CARS+self.NUM_PEDS):
            agents.append(PursuitAgent(i))
        for i in range(self.NUM_CARS+self.NUM_PEDS, self.NUM_CARS+self.NUM_PEDS+4):
            agents.append(TrafficLightAgent(i))
        for i in range(self.NUM_CARS+self.NUM_PEDS+4 , self.NUM_CARS+self.NUM_PEDS+12):
            agents.append(CrosswalkLightAgent(i))

        geoplanner = GeometricPlanner(deepcopy(state), inter_point_d=40.0, planning_time=0.1, num_cars = self.NUM_CARS)
        geo_trajs = geoplanner.plan_all_agents(state)
        for i in range(self.NUM_CARS, self.NUM_CARS+self.NUM_PEDS):
            CasteljauPlanner().plan_agent(state.dynamic_objects[i]) # used as a linear planner

        pos_trajs = [Trajectory(mode='xyva') for _ in range(self.NUM_CARS+self.NUM_PEDS)]
        action_trajs = [Trajectory(mode = 'cs') for _ in range(self.NUM_CARS+self.NUM_PEDS)]

        # Simulation loop
        for sim_time in range(self.DEMO_LEN):
            target_velocities_learner = self.il_learn.eval_model(self.NUM_CARS,state,goal_states)
            target_velocities_sup = []

            for agent_num in range(self.NUM_CARS):
                state.dynamic_objects[agent_num].trajectory.set_vel(target_velocities_learner[agent_num])
                target_vel = VelocityMPCPlanner().plan(deepcopy(state), agent_num)
                target_velocities_sup.append(target_vel)

            # Don't learn for pedestrians
            for agent_num in range(self.NUM_CARS, self.NUM_CARS + self.NUM_PEDS):
                target_vel = PedestrianVelPlanner().plan(deepcopy(state),agent_num)
                state.dynamic_objects[agent_num].trajectory.set_vel(target_vel)


            # Get all actions
           
            actions = []

            for agent in agents:
                actions.append(agent.eval_policy(state))
                
            # save old state
            state_copy = env.get_state_copy()

            # Simulate the state
            state, reward, done, info_dict = env._step_test(actions)
            env._render()

            # Log all information
            sar = {}
            sar['state'] = state_copy
            sar['reward'] = reward
            sar['action'] = actions
            sar['target_velocities_learner'] = target_velocities_learner
            sar['target_velocities_sup'] = target_velocities_sup

            rollout.append(sar)

            for i in range(self.NUM_CARS+self.NUM_PEDS):
                obj = state_copy.dynamic_objects[i]
                pos_trajs[i].add_point([obj.x, obj.y, obj.vel, obj.angle])
                action_trajs[i].add_point(actions[i])

            if self.check_success(final_state):
                break

        self.d_logger.log_info('pos_trajs', pos_trajs)
        self.d_logger.log_info('control_trajs', action_trajs)

        return rollout,deepcopy(env.current_state)

    def collect_policy_rollouts(self):
        """
        Collects a number of policy rollouts and measures success

        Returns
        ----------
        The evaulations and the reported success rate
        """
        print "called"
        policy_success_rate = 0.0
        evaluations = []
        for i in range(self.NUM_EVAL_POINTS):

            #Randomly Sample Number of Cars
            self.NUM_CARS = np.random.randint(2,self.MAX_AGENTS)
            self.NUM_PEDS = np.random.randint(2,self.MAX_AGENTS)

            rollout,final_state= self.rollout_policy()
            if self.check_success(final_state):
                policy_success_rate += 1.0
            evaluations.append(rollout)
            
      
        policy_success_rate = policy_success_rate/float(self.NUM_EVAL_POINTS)

        return evaluations, policy_success_rate

    def collect_supervisor_rollouts(self):
        """
        Collects a number of policy rollouts and measures success

        Returns
        ----------
        The recorded success rate of the planner
        """
        success_rate = 0.0

        for i in range(self.NUM_DATA_POINTS):
            #Randomly Sample Number of Cars
            self.NUM_CARS = np.random.randint(2,self.MAX_AGENTS)
            self.NUM_PEDS = np.random.randint(2,self.MAX_AGENTS)

            rollout,final_state = self.rollout_supervisor()
            if self.check_success(final_state):
                success_rate += 1.0
            
            self.d_logger.log_info('success', self.check_success(final_state))
            self.d_logger.log_info('num_cars', self.NUM_CARS)
            self.d_logger.save_rollout(rollout)

      
        self.success_rate = success_rate/float(self.NUM_DATA_POINTS)


