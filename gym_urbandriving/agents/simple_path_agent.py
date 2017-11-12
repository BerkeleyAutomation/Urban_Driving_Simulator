from copy import deepcopy
import numpy as np

class SimplePathAgent:
    def __init__(self, agent_num=0, target_loc=[450,900], collect_radius = 15, vis=None, waypoints= None):
        self.agent_num = agent_num
        self.target_loc = target_loc
        self.waypoints = waypoints
        self.current_action_index = 0
        self.collect_radius = collect_radius
        self.vis = vis
        self.action_space = [(0, 1), (3, 0), (-3, 0), (0, 0)]

        def reward_function(state, dest, wayp):
            pos = state.dynamic_objects[self.agent_num].get_pos()
            distance = np.linalg.norm( pos - dest)
            wayp = sum([max(-50, -np.linalg.norm(pos-w)) for w in wayp])
            return -distance + 10*wayp

        self.reward_fn = reward_function
        from gym_urbandriving import UrbanDrivingEnv

        self.planning_env = UrbanDrivingEnv(init_state=None)
        return

    def update_waypoints(self, old_waypoints, new_state):
        current_position = new_state.dynamic_objects[self.agent_num].get_pos()
        new_waypoints = [w for w in old_waypoints if ((w[0]-current_position[0])**2 + (w[1]-current_position[1])**2)>self.collect_radius**2]
        return new_waypoints

    def eval_policy(self, state):
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


        best_reward = 0
        best_action = None

        for action in self.action_space:
            self.planning_env._reset(state)
            next_state, _, done, info_dict = self.planning_env._step(action, self.agent_num)
            new_waypoints = self.update_waypoints(self.waypoints, next_state)
            reward = self.reward_fn(next_state, self.target_loc, new_waypoints)
            if not done and (reward > best_reward or best_action == None):
                best_action = action
                best_reward = reward
        print(str(best_action) + ",")
        return best_action
