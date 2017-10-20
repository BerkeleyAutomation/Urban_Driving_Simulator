"""

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


"""



from copy import deepcopy
import numpy as np
import queue
import gym_urbandriving as uds


class TreeSearchAgent:
    def __init__(self, agent_num=0, target_loc=[450,900], collect_radius = 10, vis=None):
        self.agent_num = agent_num
        self.target_loc = target_loc
        self.waypoints = None
        self.actions = None
        self.current_action_index = 0
        self.collect_radius = collect_radius
        self.vis = vis

        self.action_space = [(0, 1), (3, 0), (-3, 0), (0, 0)]
        def reward_function(state, dest, wayp):
            return -np.linalg.norm(state.dynamic_objects[0].get_pos() - dest) 
        self.reward_fn = reward_function
        from gym_urbandriving import UrbanDrivingEnv

        self.planning_env = UrbanDrivingEnv(init_state=None, visualizer = vis)

        return

    def update_waypoints(self, old_waypoints, new_state):
        current_position = new_state.dynamic_objects[self.agent_num].get_pos()
        new_waypoints = [w for w in old_waypoints if ((w[0]-current_position[0])**2 + (w[1]-current_position[1])**2)>self.collect_radius**2]
        return new_waypoints

    def goal_test(self, state):
        return np.linalg.norm(state.dynamic_objects[0].get_pos() - self.target_loc)<10

    def tree_search(self, curr_state):
    
        future_states = queue.PriorityQueue()
        for action in self.action_space:
            self.planning_env._reset(curr_state)
            next_state, _, done, info_dict = self.planning_env._step(action)
            new_waypoints = self.update_waypoints(self.waypoints, next_state)
            reward = self.reward_fn(next_state, self.target_loc, new_waypoints)
            if not done:
                future_states.put((-reward, np.random.random(), next_state, [action], new_waypoints))
        while True:
            old_reward, _, state, actions, waypoints = future_states.get()
            self.planning_env._reset(state)
            self.planning_env._render(state, waypoints= waypoints)
            if self.goal_test(state):
                print("goal found")
                return actions
            for next_action in self.action_space:
                self.planning_env._reset(state)
                next_state, _ , done, info_dict = self.planning_env._step(next_action)
                new_waypoints = self.update_waypoints(waypoints, next_state)
                reward = self.reward_fn(next_state, self.target_loc, new_waypoints)
                if not done:
                    future_states.put((-reward + len(actions), np.random.random(), next_state,
                                   actions + [next_action], new_waypoints))


    def eval_policy(self, state, nsteps=8):
        """
        If we can accelerate, see if we crash in nsteps.
        If we crash, decelerate, else accelerate
        """
        if self.waypoints == None:
            start_pos = state.dynamic_objects[self.agent_num].get_pos()
            if start_pos[1] < 400:
                self.waypoints = [[450,250+50*i] for i in range(10)]
                # Coming from above
                print("Coming from above")
            elif start_pos[0]<450:
                self.waypoints = [[250,550], [300,545], [350,540], [400,535],  [425,540], [440,550],[450,560] , [460,575], [465, 600], [460, 650],[455, 700],[450, 750]]
                # Coming from the left
                print("Coming from the left")
            elif start_pos[0]>450:
                self.waypoints = [[750,450], [700,450], [650,450], [600,450], [540,460], [485,485], [460,540], [450,600], [450,650], [450,700], [450,750]]
                # Coming from the right 
                print("Coming from the right")
        else:
            current_position = state.dynamic_objects[self.agent_num].get_pos()
            self.waypoints = [w for w in self.waypoints if ((w[0]-current_position[0])**2 + (w[1]-current_position[1])**2)>self.collect_radius**2]

        if self.actions == None:
            self.current_action_index = 0
            print("tree searching")
            self.actions = self.tree_search(deepcopy(state))
        
        if self.current_action_index < len(self.actions):
            ret_val = self.actions[self.current_action_index]
            self.current_action_index += 1
            return ret_val
        return None

