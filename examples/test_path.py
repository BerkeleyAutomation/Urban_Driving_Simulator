import gym
import gym_urbandriving as uds
import cProfile
import time

from gym_urbandriving.agents import KeyboardAgent, AccelAgent, NullAgent, SimplePathAgent

import numpy as np
import pygame

def test_path():
    """
    Main function to be run to test simple_path_agent with hard coded path. 

    Examples
    --------
    python3 examples/test_path.py

    """

    vis = uds.PyGameVisualizer((800, 800))
    init_state = uds.state.SimpleIntersectionState(ncars=1, nped=0)

    env = uds.UrbanDrivingEnv(init_state=init_state,
                              visualizer=vis,
                              bgagent=SimplePathAgent,
                              max_time=250,
                              randomize=True,
                              nthreads=4)

    env._render()
    state = init_state
    agent = SimplePathAgent()
    action = None
    while(True):
        action = agent.eval_policy(state)
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
  test_path()
