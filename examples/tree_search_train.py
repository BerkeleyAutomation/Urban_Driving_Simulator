import gym
import gym_urbandriving as uds
import cProfile
import time

from gym_urbandriving.agents import  NullAgent, TreeSearchAgent, SimplePathAgent, AccelAgent

import numpy as np
import pygame
from copy import deepcopy
from random import random

from gym_urbandriving.assets import Car
from gym_urbandriving.agents import AccelAgent, KeyboardAgent, NullAgent

def run():
    """
    Main function to be run to test simple_path_agent with hard coded path.

    Examples
    --------
    python3 examples/test_path.py

    """

    vis = uds.PyGameVisualizer((800, 800))
    init_state = uds.state.SimpleIntersectionState(ncars=2, nped=0)


    env = uds.UrbanDrivingEnv(init_state=None,
                              visualizer=vis,
                              agent_mappings={Car:NullAgent},
                              max_time=-1,
                              randomize=False,
    )

    env._reset()
    state = env.current_state
    agent = TreeSearchAgent()
    action = None

    while(True):
        action = agent.eval_policy(deepcopy(state))
        start_time = time.time()
        state, reward, done, info_dict = env._step(action)

        env._render(waypoints = agent.waypoints)
        if done:
            print("done")
            time.sleep(1)
            print(info_dict["dynamic_collisions"])
            env._reset()
            state = env.current_state
            agent.waypoints = None
            agent.actions = None


if __name__ == "__main__":
  run()
