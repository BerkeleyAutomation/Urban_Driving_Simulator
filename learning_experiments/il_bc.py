import gym
import gym_urbandriving as uds
import cProfile
import time
import numpy as np
import numpy.linalg as LA

from gym_urbandriving.agents import KeyboardAgent, AccelAgent, NullAgent, TrafficLightAgent, RRTMAgent, RRTMPlanner
from gym_urbandriving.assets import Car, TrafficLight
from gym_urbandriving.utils.data_logger import DataLogger
from gym_urbandriving.learner.imitation_learner import IL
from gym_urbandriving.learner.trainer import Trainer
from gym_urbandriving.learner.plotter import Plotter



NUM_DATA_PER_ITER = 2
NUM_EVAL_POINTS = 5
NUM_ITERS = 2
TIME_HORIZON = 100
PLANNING_TIME = 0.5


FILE_PATH = 'test_data/'

ALG_NAME = 'B_C'
FILE_PATH_ALG =  FILE_PATH + ALG_NAME 

t_exp = Trainer(FILE_PATH_ALG,
                num_data_points = NUM_DATA_PER_ITER, 
                num_eval_points = NUM_EVAL_POINTS,
                time_horizon = TIME_HORIZON,
                time = PLANNING_TIME)

plotter = Plotter(ALG_NAME,FILE_PATH_ALG)
stats = []

for i in range(NUM_ITERS):

    t_exp.collect_supervisor_rollouts()
    t_exp.train_model()
    stats.append(t_exp.get_stats())


plotter.save_plots(stats)












