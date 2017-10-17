import gym
import gym_urbandriving as uds
import cProfile
import time
import numpy as np
import pickle

from gym_urbandriving.agents import AccelAgent

def early_stop_actions(actions):
    """
    Helper function used to determine if list of actions indicates that a demonstration can be terminated early. 

    Params
    --------
    actions : list
        List of actions taken by all the agents in a time step. 

    Returns
    -------
    bool
        True if approximately all the cars have gone through the intersection and are back up to speed. 

    """
    return actions == [(0, 1), (0, 1), (0, 1), (0, 1)]

def run_and_collect():
    """
    Main function to be run to collect driving data. 
    Make sure that a data folder exists in the root directory of the project!

    Examples
    --------
    python3 examples/collect_data.py

    """

    saved_states = []
    saved_actions = []

    vis = uds.PyGameVisualizer((800, 800))
    init_state = uds.state.SimpleIntersectionState(ncars=4, nped=0)

    env = uds.UrbanDrivingEnv(init_state=init_state,
                              visualizer=vis,
                              bgagent=AccelAgent,
                              max_time=100,
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
        if early_stop_actions(info_dict["saved_actions"]): 
            reset_counter+=1
        else:
            reset_counter = 0

        env._render()

        if done or reset_counter >50:
            # Time to save our current run and reset our env and our saved data
            reset_counter = 0

            pickle.dump((saved_states, saved_actions),open("data/"+str(np.random.random())+"dump.data", "wb+"))

            print("done")
            print(info_dict["dynamic_collisions"])

            env._reset()
            state = env.current_state
            
            saved_states = []
            saved_actions = []

if __name__ == "__main__":
  run_and_collect()
