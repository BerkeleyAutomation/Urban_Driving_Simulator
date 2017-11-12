from copy import deepcopy
import numpy as np
import queue
import gym_urbandriving as uds
from gym_urbandriving.agents import NullAgent, AccelAgent

class TreeSearchAgent:
    def __init__(self, agent_num=0, target_loc=[450,900], collect_radius = 15, vis=None):
        self.agent_num = agent_num
        self.target_loc = target_loc
        self.waypoints = None
        self.actions = None
        self.current_action_index = 0
        self.collect_radius = collect_radius
        self.vis = vis

        self.action_space = [(0, 1), (3, 0), (-3, 0)]

        def reward_function(state, dest, wayp):
            pos = state.dynamic_objects[0].get_pos()
            distance = np.linalg.norm( pos - dest)
            wayp = sum([max(-50, -np.linalg.norm(pos-w)) for w in wayp])
            log_coll = np.log(state.min_dist_to_coll(self.agent_num))
            return -distance + 25*wayp + 100*log_coll

        self.reward_fn = reward_function
        from gym_urbandriving import UrbanDrivingEnv

        self.planning_env = UrbanDrivingEnv(init_state=None, bgagent=AccelAgent, visualizer = vis)

        self.planning_threshold = 500 # If solution isn't found within threshold number of steps, give up
        return

    def update_waypoints(self, old_waypoints, new_state):
        current_position = new_state.dynamic_objects[self.agent_num].get_pos()
        new_waypoints = [w for w in old_waypoints if ((w[0]-current_position[0])**2 + (w[1]-current_position[1])**2)>self.collect_radius**2]
        return new_waypoints

    def goal_test(self, state):
        return np.linalg.norm(state.dynamic_objects[0].get_pos() - self.target_loc)<10

    def tree_search(self, curr_state):
        steps = 0

        future_states = queue.PriorityQueue()
        for action in self.action_space:
            self.planning_env._reset(curr_state)
            next_state, _, done, info_dict = self.planning_env._step(action)
            new_waypoints = self.update_waypoints(self.waypoints, next_state)
            reward = self.reward_fn(next_state, self.target_loc, new_waypoints)
            if not done:
                future_states.put((-reward, np.random.random(), next_state, [action], new_waypoints))
        while True:
            steps += 1
            if steps > self.planning_threshold:
                break

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


        return None

    def eval_policy(self, state, nsteps=8):
        """
        If we can accelerate, see if we crash in nsteps.
        If we crash, decelerate, else accelerate
        """
        if self.waypoints == None:
            start_pos = state.dynamic_objects[self.agent_num].get_pos()
            if start_pos[1] < 400:
                self.waypoints = [[450,250+50*i] for i in range(10)]
                self.waypoints = [w for w in self.waypoints if w[1]>start_pos[1]]
                # Coming from above
                print("Coming from above")
            elif start_pos[0]<450:
                self.waypoints = [[250,550], [300,545], [350,540], [400,535],  [415,540], [430,550], [440,560], [450,575], [455, 600], [450, 650],[450, 700],[450, 750]]
                self.waypoints = [w for w in self.waypoints if w[0]>start_pos[0]]
                # Coming from the left
                print("Coming from the left")
            elif start_pos[0]>450:
                self.waypoints = [[750,450], [700,450], [650,450], [600,450], [540,460], [485,485], [460,540], [450,600], [450,650], [450,700], [450,750]]
                self.waypoints = [w for w in self.waypoints if w[0]<start_pos[0]]
                # Coming from the right 
                print("Coming from the right")
        else:
            current_position = state.dynamic_objects[self.agent_num].get_pos()
            self.waypoints = [w for w in self.waypoints if ((w[0]-current_position[0])**2 + (w[1]-current_position[1])**2)>self.collect_radius**2]

        if self.actions == None:
            self.current_action_index = 0
            print("tree searching")
            self.actions = self.tree_search(deepcopy(state))
            if self.actions == None: # still no solution found, 
                self.actions = []
                

        if self.current_action_index < len(self.actions):
            ret_val = self.actions[self.current_action_index]
            self.current_action_index += 1
            return ret_val
        return None

