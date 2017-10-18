import gym
import gym_urbandriving as uds
import cProfile
import time
import numpy as np
import pickle
import os
import ray
import queue
import pygame
from copy import deepcopy
from random import random
from gym_urbandriving.agents import AccelAgent, KeyboardAgent, NullAgent

saved_states = []
saved_actions = []

vis = uds.PyGameVisualizer((800, 800))
env = uds.UrbanDrivingEnv(init_state=None,
                          visualizer=vis,
                          bgagent=NullAgent,
                          max_time=-1,
                          randomize=False,
)
action_space = [(0, 1), (3, 0), (-3, 0), (0, 0)]

reward_fn = lambda dest: lambda state:\
            -np.linalg.norm(state.dynamic_objects[0].get_pos() - dest)
steps_expanded = 0

def tree_search(state, destination):
    global steps_expanded
    steps_expanded += 1
    future_states = queue.PriorityQueue()
    for action in action_space:
        env._reset(state)
        next_state, reward, done, info_dict = env._step(action)
        if done:
            reward = reward - 99999
        future_states.put((-reward, random(), next_state, [action]))
    while True:
        best_reward, _, state, actions = future_states.get()
        env._reset(state)
        env._render(state)
        if reward_fn(destination)(state) > -10:
            return actions
        for next_action in action_space:
            env._reset(state)
            next_state, reward, done, info_dict = env._step(next_action)
            if done:
                reward = reward - 99999
            future_states.put((-reward + len(actions), random(), next_state,
                               actions + [next_action]))

action = None
while(True):
    destination = [450, 1000]
    env.reward_fn = reward_fn(destination)
    steps_expanded = 0
    init_state = uds.state.SimpleIntersectionState(ncars=1, nped=0)
    env._reset(init_state)
    env._render()
    actions = tree_search(deepcopy(init_state), destination)
    env._reset(init_state)
    s = init_state
    for action in actions:
        s, r, d, i = env._step(action)
        env._render()
