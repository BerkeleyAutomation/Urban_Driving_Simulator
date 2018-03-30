import gym_urbandriving as uds
from gym_urbandriving.state.state import PositionState
from gym_urbandriving.assets import Terrain, Lane, Street, Sidewalk,\
    Pedestrian, Car, TrafficLight

from gym_urbandriving.agents import KeyboardAgent, AccelAgent, NullAgent, TrafficLightAgent, CrosswalkLightAgent,  PursuitAgent, ControlAgent, PlanningPursuitAgent
from gym_urbandriving.planning import Trajectory, CasteljauPlanner, GeometricPlanner, VelocityMPCPlanner

from gym_urbandriving.assets import Car, TrafficLight, Pedestrian, CrosswalkLight

from copy import deepcopy
import pickle

import numpy as np
import os
import glob
from sklearn.tree import DecisionTreeRegressor
from sklearn.tree import DecisionTreeClassifier
from numpy.random import uniform
import numpy.linalg as LA
from gym_urbandriving.utils.data_logger import DataLogger
from gym_urbandriving.utils.featurizer import Featurizer

X_train = []
Y_train = []
Y_train_traj_vel = []

FILES_PATH = "test_data/KIN_DYN_TRAJS"
data_logger = DataLogger(FILES_PATH)

vis = uds.PyGameVisualizer((800, 800))
featurizer = Featurizer()
# for index in range(200):
#     print(index)
#     loaded_rollout = data_logger.load_rollout(index)
#     num_cars = loaded_rollout[1]['num_cars']
#     goal_states = loaded_rollout[1]['goal_states']
#     success = loaded_rollout[1]['success']
#     agent_ids = loaded_rollout[1]['agent_ids']
#     states = loaded_rollout[0]
#     n_states = len(loaded_rollout[0])
#     print(agent_ids, loaded_rollout[0][0])
#     vis.render(states[0]['state'], [0, 1000, 0, 1000])
#     for i, agent_num in enumerate(agent_ids):
#         print(i)
#         for t in range(n_states - 1):
#             c_state = states[t]
#             #p_state = states[t-1]
#             features = featurizer.featurize(c_state['state'], agent_num)
#             action = c_state['action'][i]
#             traj_vel = c_state['state'].dynamic_objects[agent_num].trajectory
#             if features:
#                 X_train.append(features)
#                 Y_train.append(action)
#                 Y_train_traj_vel.append(traj_vel.get_point(0)[2])
# print(len(X_train))
# model = DecisionTreeRegressor()
# model_classifier = DecisionTreeClassifier()
# Y_train = np.array(Y_train)
# Y_train_traj_vel = np.array(Y_train_traj_vel)


# model.fit(X_train, Y_train)
# model_classifier.fit(X_train, Y_train_traj_vel)

# pickle.dump(model, open("model.model", "wb"))
# pickle.dump(model_classifier, open("model_classifier.model", "wb"))
model = pickle.load(open("model.model"))
model_classifier = pickle.load(open("model_classifier.model"))
NUM_CARS = 4
init_state = uds.state.SimpleIntersectionState(ncars=NUM_CARS, nped=0, traffic_lights=True)


geoplanner = GeometricPlanner(deepcopy(init_state), inter_point_d=40.0, planning_time=0.1, num_cars = NUM_CARS)
geoplanner.plan_all_agents(init_state)

sim_time = 0
env = uds.UrbanDrivingEnv(init_state=deepcopy(init_state),
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
for i in range(NUM_CARS):
    agents.append(PursuitAgent(i))
for i in range(NUM_CARS, NUM_CARS + 4):
    agents.append(TrafficLightAgent(i))
for i in range(NUM_CARS+4, NUM_CARS + 12):
    agents.append(CrosswalkLightAgent(i))

#prev_state = deepcopy(state)
for sim_time in range(500):
    actions = [None] * len(agents)
    
    # for agent_num in range(NUM_CARS):
    #     target_vel = VelocityMPCPlanner().plan(deepcopy(state), agent_num)
    #     state.dynamic_objects[agent_num].trajectory.set_vel(target_vel)

    for i in range(NUM_CARS):
        features = featurizer.featurize(state, i)

        if features is not None:
            pred = model.predict([features])
            acc_pred = model_classifier.predict([features])
            steer, acc = pred[0][0], pred[0][1]
            state.dynamic_objects[i].trajectory.set_vel(acc_pred)
        else:
            steer, acc = 0, 0
            
        action = PursuitAgent(i).eval_policy(state)
        #steer = action[0]
        actions[i] = action
        #actions[i] = (steer, acc)
    for i in range(NUM_CARS, NUM_CARS+12):
        actions[i] = (agents[i].eval_policy(state))
        # Simulate the state
    prev_state = deepcopy(state)
    state, reward, done, info_dict = env._step_test(actions)
    
    env._render()
