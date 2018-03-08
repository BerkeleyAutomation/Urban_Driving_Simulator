from gym_urbandriving.learner.trainer import Trainer
import numpy as np

###A script to test behavior cloning 

##PARAMTERS FOR THE EXPERIMENT
NUM_DATA_PER_ITER = 2 #NUMBER OF TRAJECTORIES TO SAMPLE FROM THE SUPERVISOR 
NUM_EVAL_POINTS = 1 #NUMBER OF TRAJECTORIES TO SAMPLE FROM THE LEANRED POLICY (i.e. for Evaluation) 
NUM_ITERS = 1 #NNumber of iterations 
TIME_HORIZON = 100 #Time horizon for the learned policy
PLANNING_TIME = 50 #planning time limit for the supervisor 
MAX_AGENTS = 5
#Path to save data

FILE_PATH = 'test_data/'

#Specifc experiment 
ALG_NAME = 'KIN_DYN_TRAJS'
FILE_PATH_ALG =  FILE_PATH + ALG_NAME 

#Trainer class
t_exp = Trainer(FILE_PATH_ALG,
                num_data_points = NUM_DATA_PER_ITER, 
                num_eval_points = NUM_EVAL_POINTS,
                time_horizon = TIME_HORIZON,
                time = PLANNING_TIME,
                max_agents = MAX_AGENTS)

for i in range(NUM_ITERS):
    #Collect demonstrations 
    t_exp.collect_supervisor_rollouts()












