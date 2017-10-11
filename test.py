import gym
import gym_urbandriving as uds
import cProfile
import time

from gym_urbandriving.assets import Terrain, Lane, Street, Sidewalk, KinematicCar, Pedestrian, Car
from gym_urbandriving.agents import ModelAgent, KeyboardAgent, SimpleAvoidanceAgent, AccelAgent, NullAgent

import numpy as np
import pickle
import time


def vectorize_state(state):
    state_vec = []
    for obj in state.dynamic_objects:
        state_vec.append(np.array([(obj.x-500)/500, (obj.y-500)/500, (obj.vel-10)/10]))
    return state_vec

def f():
    saved_states = []
    saved_actions = []
    accs = 0
    totalticks = 0
    num_exps = 0
    start_time = time.time()

    vis = uds.PyGameVisualizer((800, 800))
    init_state = uds.state.ArenaState(ncars=5, nped=0)

    env = uds.UrbanDrivingEnv(init_state=init_state,
                              visualizer=vis,

                              bgagent=AccelAgent,
                              max_time=250,
                              randomize=True,
                              nthreads=4)
    env._render()
    state = init_state
    agent = ModelAgent()
    reset_counter = 0
    
    action = None
    while(True):
        action = agent.eval_policy(state)
        saved_states.append(vectorize_state(state))
        start_time = time.time()
        state, reward, done, info_dict = env._step(action)
        #print(info_dict["saved_actions"])
        saved_actions.append(info_dict["saved_actions"])
        
        if info_dict["saved_actions"] == [(0, 1), (0, 1), (0, 1), (0, 1)]:
            reset_counter+=1
        else:
            reset_counter = 0

        totalticks += 1
        env._render()
        
        if done or reset_counter >10:
            reset_counter = -10
            
            if type(agent) is AccelAgent:
                pickle.dump((saved_states, saved_actions),open("data/"+str(np.random.random())+"dump.data", "wb+"))
            
            print("done")
            print((time.time()-start_time)/totalticks, totalticks)
            print(info_dict["dynamic_collisions"])
            
            if type(agent) is ModelAgent:
              accs += info_dict["predict_accuracy"]
              #print(accs/totalticks)
              num_exps += 1
              if num_exps == 131:
                  exit

            env._reset()
            saved_states = []
            saved_actions = []

cProfile.run('f()', 'stats')
