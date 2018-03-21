import gym
import gym_urbandriving as uds
import cProfile
import time
import numpy as np
import math
import random
import timeit

from gym_urbandriving.agents import AccelAgent, NullAgent, TrafficLightAgent, CrosswalkLightAgent,  PursuitAgent, ControlAgent, PlanningPursuitAgent
from gym_urbandriving.planning import Trajectory, CasteljauPlanner, GeometricPlanner, VelocityMPCPlanner

from gym_urbandriving.assets import Car, TrafficLight, Pedestrian, CrosswalkLight

from copy import deepcopy

from multiprocessing import Pool

import pickle

from gym_urbandriving.utils.featurizer import Featurizer

import tblib.pickling_support
tblib.pickling_support.install()


import sys


class ExceptionWrapper(object):

    def __init__(self, ee):
        self.ee = ee
        __,  __, self.tb = sys.exc_info()

    def re_raise(self):
        raise self.ee, None, self.tb

        #raise self.ee.with_traceback(self.tb)

"""
 Test File, to demonstrate general functionality of environment
"""

#NUM_CARS = 4
#NUM_PEDS = 0
#DEMO_LEN = 300
THRESH = 280
def check_success(state):
    # returns to break and if success
    state_copy = deepcopy(state)
    for agent_num,obj in enumerate(state_copy.dynamic_objects):
        if type(obj) in {Car}:
            if state_copy.collides_any_dynamic(agent_num):
                return True, False
            if np.linalg.norm(np.array([obj.x, obj.y]) - np.array([obj.destination[0], obj.destination[1]])) > THRESH and not obj.trajectory.is_empty():
                return False, False
    return True, True

def g(NUM_CARS, NUM_PEDS = 0, DEMO_LEN = 400):
    try:
            num_samples = 0
            # Instantiate a PyGame Visualizer of size 800x800
            #vis = uds.PyGameVisualizer((800, 800))

            # Create a simple-intersection state, with 4 cars, no pedestrians, and traffic lights
            init_state = uds.state.SimpleIntersectionState(ncars=NUM_CARS, nped=NUM_PEDS, traffic_lights=True)

            env = uds.UrbanDrivingEnv(init_state=init_state,
                                      visualizer=None,
                                      max_time=500,
                                      randomize=False,
                                      agent_mappings={Car:NullAgent,
                                                      TrafficLight:TrafficLightAgent},
                                      use_ray=False
            )

            env._reset()
            state = env.current_state

            geoplanner = GeometricPlanner(deepcopy(state), inter_point_d=40.0, planning_time=0.1, num_cars = NUM_CARS)
            geoplanner.plan_all_agents(state)
            for i in range(NUM_CARS, NUM_CARS+NUM_PEDS):
                CasteljauPlanner().plan_agent(state.dynamic_objects[i]) # linear planner

            sim_time = 0

            model_classifier = pickle.load(open("model_classifier_exp0.model"))
            featurizer = Featurizer()

            action_trajs = [Trajectory(mode = 'cs') for _ in range(NUM_CARS+NUM_PEDS)]   


            agents = []
            for i in range(NUM_CARS+NUM_PEDS):
                agents.append(PursuitAgent(i))
            for i in range(NUM_CARS + NUM_PEDS, NUM_CARS + NUM_PEDS + 4):
                agents.append(TrafficLightAgent(i))
            for i in range(NUM_CARS + NUM_PEDS + 4, NUM_CARS + NUM_PEDS + 12):
                agents.append(CrosswalkLightAgent(i))


            for sim_time in range(DEMO_LEN):
                actions = [] 

                for agent_num in range(NUM_CARS+NUM_PEDS):
                    #target_vel = VelocityMPCPlanner().plan(deepcopy(state), agent_num)
                    features = featurizer.featurize(state,agent_num)
                    if features is None:
                       continue
                    target_vel = model_classifier.predict([features])[0]
                    #print(target_vel)
                    state.dynamic_objects[agent_num].trajectory.set_vel(target_vel)

                for agent in agents:
                    action = agent.eval_policy(state)
                    actions.append(action)
                    if not action is None:
                        num_samples += 1
                    
                # Simulate the state
                state, reward, done, info_dict = env._step_test(actions)
                env._render()
                for i in range(NUM_CARS+NUM_PEDS):
                    action_trajs[i].add_point(info_dict['saved_actions'][i])

                break_flag, break_success = check_success(state)
                if break_flag:
                    break

            if break_success:
                return num_samples, num_samples, True
            else:
                return num_samples, 0, False
    except Exception as e:
        return ExceptionWrapper(e)

def f(NUM_CARS, NUM_PEDS = 0, DEMO_LEN = 400):
    num_samples = 0
    # Instantiate a PyGame Visualizer of size 800x800
    #vis = uds.PyGameVisualizer((800, 800))

    # Create a simple-intersection state, with 4 cars, no pedestrians, and traffic lights
    init_state = uds.state.SimpleIntersectionState(ncars=NUM_CARS, nped=NUM_PEDS, traffic_lights=True)

    env = uds.UrbanDrivingEnv(init_state=init_state,
                              visualizer=None,
                              max_time=500,
                              randomize=False,
                              agent_mappings={Car:NullAgent,
                                              TrafficLight:TrafficLightAgent},
                              use_ray=False
    )

    env._reset()
    state = env.current_state

    geoplanner = GeometricPlanner(deepcopy(state), inter_point_d=40.0, planning_time=0.1, num_cars = NUM_CARS)
    geoplanner.plan_all_agents(state)
    for i in range(NUM_CARS, NUM_CARS+NUM_PEDS):
        CasteljauPlanner().plan_agent(state.dynamic_objects[i]) # linear planner

    sim_time = 0

    action_trajs = [Trajectory(mode = 'cs') for _ in range(NUM_CARS+NUM_PEDS)]   


    agents = []
    for i in range(NUM_CARS+NUM_PEDS):
        agents.append(PursuitAgent(i))
    for i in range(NUM_CARS + NUM_PEDS, NUM_CARS + NUM_PEDS + 4):
        agents.append(TrafficLightAgent(i))
    for i in range(NUM_CARS + NUM_PEDS + 4, NUM_CARS + NUM_PEDS + 12):
        agents.append(CrosswalkLightAgent(i))


    for sim_time in range(DEMO_LEN):
        actions = [] 

        for agent_num in range(NUM_CARS+NUM_PEDS):
            target_vel = VelocityMPCPlanner().plan(deepcopy(state), agent_num)
            #features = featurizer.featurize(state,agent_num)
            #target_vel = model_classifier.predict([features])[0]
            #print(target_vel)
            state.dynamic_objects[agent_num].trajectory.set_vel(target_vel)

        for agent in agents:
            action = agent.eval_policy(state)
            actions.append(action)
            if not action is None:
                num_samples += 1
            
        # Simulate the state
        state, reward, done, info_dict = env._step_test(actions)
        env._render()
        for i in range(NUM_CARS+NUM_PEDS):
            action_trajs[i].add_point(info_dict['saved_actions'][i])

        break_flag, break_success = check_success(state)
        if break_flag:
            break

    if break_success:
        return num_samples, num_samples, True
    else:
        return num_samples, 0, False

if __name__ == "__main__":
    """
    non_parallel_sample_count = []
    non_parallel_times = []

    for n_c in range(2,8):
        n_c_samples = []
        n_c_times = []
        for n_samples in range(10):
            start = timeit.default_timer()
            n_c_samples.append(f(n_c))
            end = timeit.default_timer()
            n_c_times.append(end-start)
        non_parallel_sample_count.append(n_c_samples)
        non_parallel_times.append(n_c_times)
        print(non_parallel_sample_count)
        print(non_parallel_times)

    pickle.dump([non_parallel_sample_count, non_parallel_times], open("timing_stats_sup1.pickle", "wb"))

    parallel_sample_count = []
    parallel_times = []

    for n_c in range(2,10):
        n_c_samples = []
        n_c_times = []
        for n_samples in range(10):
            start = timeit.default_timer()
            p = Pool(10)
            n_c_samples.append(p.map(f, [n_c for _ in range(10)]))
            end = timeit.default_timer()
            n_c_times.append(end-start)
        parallel_sample_count.append(n_c_samples)
        parallel_times.append(n_c_times)
        print(parallel_sample_count)
        print(parallel_times)
        pickle.dump([parallel_sample_count, parallel_times], open("timing_stats_sup2_"+str(n_c)+".pickle", "wb"))

    pickle.dump([parallel_sample_count, parallel_times], open("timing_stats_sup2.pickle", "wb"))

    non_parallel_sample_count = []
    non_parallel_times = []

    for n_c in range(2,8):
        n_c_samples = []
        n_c_times = []
        for n_samples in range(10):
            start = timeit.default_timer()
            n_c_samples.append(g(n_c))
            end = timeit.default_timer()
            n_c_times.append(end-start)
        non_parallel_sample_count.append(n_c_samples)
        non_parallel_times.append(n_c_times)
        print(non_parallel_sample_count)
        print(non_parallel_times)

    pickle.dump([non_parallel_sample_count, non_parallel_times], open("timing_stats_il1.pickle", "wb"))
    """
    parallel_sample_count = []
    parallel_times = []

    for n_c in range(2,10):
        n_c_samples = []
        n_c_times = []
        for n_samples in range(10):
            start = timeit.default_timer()
            p = Pool(10)
            results = p.map(g, [n_c for _ in range(10)])
            for r in results:
                if isinstance(r, ExceptionWrapper):
                        r.re_raise()
            n_c_samples.append(results)
            end = timeit.default_timer()
            n_c_times.append(end-start)
        parallel_sample_count.append(n_c_samples)
        parallel_times.append(n_c_times)
        print(parallel_sample_count)
        print(parallel_times)
        pickle.dump([parallel_sample_count, parallel_times], open("timing_stats_il2_"+str(n_c)+".pickle", "wb"))

    pickle.dump([parallel_sample_count, parallel_times], open("timing_stats_il2.pickle", "wb"))
