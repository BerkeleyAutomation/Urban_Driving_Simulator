import gym
import gym_urbandriving as uds
import cProfile
import time
import numpy as np
import pickle

from gym_urbandriving.agents import AccelAgent

def f():
    saved_states = []
    saved_actions = []

    vis = uds.PyGameVisualizer((800, 800))
    init_state = uds.state.SimpleIntersectionState()

    env = uds.UrbanDrivingEnv(init_state=init_state,
                              visualizer=vis,
                              bgagent=AccelAgent,
                              max_time=250,
                              randomize=True,
                              nthreads=4)
    env._render()
    state = init_state
    agent = AccelAgent()
    reset_counter = 0

    action = None
    while(True):
        action = agent.eval_policy(state)
        saved_states.append(state.vectorize_state())
        start_time = time.time()
        state, reward, done, info_dict = env._step(action)
        saved_actions.append(info_dict["saved_actions"])

        # TODO: fix this line, it used to be used to shorten demos by stopping the sim after enough cars came back up to speed.
        if info_dict["saved_actions"] == [(0, 1), (0, 1), (0, 1), (0, 1)]: 
            reset_counter+=1
        else:
            reset_counter = 0

        env._render()

        if done or reset_counter >10:
            reset_counter = -10

            pickle.dump((saved_states, saved_actions),open("data/"+str(np.random.random())+"dump.data", "wb+"))

            print("done")
            print(info_dict["dynamic_collisions"])

            env._reset()
            saved_states = []
            saved_actions = []

cProfile.run('f()', 'stats')
