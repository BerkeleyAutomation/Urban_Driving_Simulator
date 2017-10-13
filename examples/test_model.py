import gym
import gym_urbandriving as uds
import cProfile
import time
import numpy as np
import pickle

from gym_urbandriving.agents import ModelAgent

def f():
    accs = 0
    totalticks = 0
    start_time = time.time()

    vis = uds.PyGameVisualizer((800, 800))
    init_state = uds.state.SimpleIntersectionState()

    env = uds.UrbanDrivingEnv(init_state=init_state,
                              visualizer=vis,
                              bgagent=ModelAgent,
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
        start_time = time.time()
        state, reward, done, info_dict = env._step(action)

        # TODO: fix this line to be consistent with changes in collect_data
        if info_dict["saved_actions"] == [(0, 1), (0, 1), (0, 1), (0, 1)]:
            reset_counter+=1
        else:
            reset_counter = 0

        totalticks += 1
        env._render()
        
        if done or reset_counter >10:
            reset_counter = -10
                        
            print("done")
            print((time.time()-start_time)/totalticks, totalticks)
            print(info_dict["dynamic_collisions"])
            
            accs += info_dict["predict_accuracy"]
            print(accs/totalticks)

            env._reset()

cProfile.run('f()', 'stats')
