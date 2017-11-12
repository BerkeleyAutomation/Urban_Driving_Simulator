import gym
import gym_urbandriving as uds
import cProfile
import time

from gym_urbandriving.agents import  NullAgent, TreeSearchAgent, AccelAgent

import numpy as np
import pygame
from copy import deepcopy

def run():
    """
    Main function to be run to test simple_path_agent with hard coded path. 

    Examples
    --------
    python3 examples/tree_search_train.py

    """

    vis = uds.PyGameVisualizer((800, 800))
    init_state = uds.state.SimpleIntersectionState(ncars=3, nped=0)


    env = uds.UrbanDrivingEnv(init_state=init_state,
                              visualizer=vis,
                              bgagent=AccelAgent,
                              max_time=250,
                              randomize=True,
                              use_ray=True)

    env._reset()
    state = env.current_state

    # To see the training in action
    agent = TreeSearchAgent(vis = vis)

    action = None

    while(True):
        action = agent.eval_policy(deepcopy(state))
        start_time = time.time()
        state, reward, done, info_dict = env._step(action)

        env._render(waypoints = agent.waypoints)
        if done:
            print("done")
            time.sleep(1)
            env._reset()
            state = env.current_state

            # reset agent state
            agent.waypoints = None
            agent.actions = None


if __name__ == "__main__":
  run()
