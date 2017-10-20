from copy import deepcopy
import numpy as np

class SimplePathAgent:
    def __init__(self, agent_num=0, target_loc=[450,900], collect_radius = 10):
        self.agent_num = agent_num
        self.target_loc = target_loc
        self.waypoints = None
        self.collect_radius = collect_radius
        return

    def eval_policy(self, state, nsteps=8):
        """
        If we can accelerate, see if we crash in nsteps.
        If we crash, decelerate, else accelerate
        """
        if self.waypoints == None:
            start_pos = state.dynamic_objects[self.agent_num].get_pos()
            x_vals = []
            y_vals = []
            intermediate_pos = [0,0]

            if start_pos[1] < 400:
                intermediate_pos = [450,450]
                y_vals = np.arange(start_pos[1], intermediate_pos[1], 10)
                x_vals = np.linspace(start_pos[0], intermediate_pos[0] , y_vals.size)
                print('case1')
            elif start_pos[0]<450:
                intermediate_pos = [450,550]
                x_vals = np.arange(start_pos[0], intermediate_pos[0],10)
                y_vals = np.linspace(start_pos[1], intermediate_pos[1], x_vals.size)
                print('case2')
            elif start_pos[0]>450:
                intermediate_pos = [450,450]
                x_vals = np.arange(intermediate_pos[0],start_pos[0],10)
                y_vals = np.linspace(intermediate_pos[1], start_pos[1], x_vals.size)
                print('case3')

            y_finish = np.arange(intermediate_pos[1], self.target_loc[1],10)
            self.waypoints = [[x_vals[i], y_vals[i]] for i in range(x_vals.size)]
            self.waypoints.extend([[self.target_loc[0], y_finish[i]] for i in range(y_finish.size)])

        else:
            current_position = state.dynamic_objects[self.agent_num].get_pos()
            self.waypoints = [w for w in self.waypoints if ((w[0]-current_position[0])**2 + (w[1]-current_position[1])**2)>self.collect_radius**2]

        from gym_urbandriving import UrbanDrivingEnv
        planning_env = UrbanDrivingEnv(init_state=state)
        start_pos = state.dynamic_objects[self.agent_num].get_pos()
        actions = [(1,1), (0,1), (-1,1), 
                    (1,-1), (0,-1), (-1,-1)]

        best_action = None
        best_reward = 0

        for action in actions:
            planning_env._reset()
            next_state, r, done, info_dict = planning_env._step(action,
                                                                self.agent_num,
                                                                copy_state=False)

            next_pos = next_state.dynamic_objects[self.agent_num].get_pos()
            waypoints_collected = len([w for w in self.waypoints if ((w[0]-next_pos[0])**2 + (w[1]-next_pos[1])**2)<= self.collect_radius**2])
            time_to_collision = 1
            for i in range(nsteps):
                next_state, r, done, info_dict = planning_env._step(action,
                                                                    self.agent_num,
                                                                    copy_state=False)
                waypoints_collected += len([w for w in self.waypoints if ((w[0]-next_pos[0])**2 + (w[1]-next_pos[1])**2)<= self.collect_radius**2])

                if (done and next_state.collides_any(self.agent_num)):
                    time_to_collision = i
                    break

            distance_to_goal = ((self.target_loc[0]-next_pos[0])**2 + (self.target_loc[1]-next_pos[1])**2)**.5
            print(distance_to_goal)
            reward  = 1000*waypoints_collected + time_to_collision - distance_to_goal/1000
            if reward > best_reward or best_action == None:
                best_action = action
                best_reward = reward

            print(best_reward)
            print(best_action)
        return best_action
