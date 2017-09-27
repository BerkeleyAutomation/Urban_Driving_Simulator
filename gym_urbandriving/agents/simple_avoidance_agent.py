from gym_urbandriving.state import PositionState
from copy import deepcopy
import numpy as np

class SimpleAvoidanceAgent:
    def __init__(self, agent_num=0, goal_pos=(500,600)):
        """
        creates a simple one step lookahead collision avoidance agent that tries to end up at its goal_pos
        """
        self.agent_num = agent_num
        self.goal_pos = goal_pos
        return
    
    def eval_policy(self, state):
        """
        checks one step in the future assuming all other objects don't take any action
        """
        
        best_reward = 0
        best_action = None
        for acc in [-1,0,1]:
            for steer in [0,0,0]:
                planning_state = deepcopy(state)
                for i in range(len(planning_state.dynamic_objects)):
                    if i == self.agent_num:
                        planning_state.dynamic_objects[i].step((steer,acc))
                    else:
                        planning_state.dynamic_objects[i].step(None)
                agent_reward = self.reward(planning_state)
                if best_action is None or agent_reward > best_reward:
                    best_action = (steer,acc)
                    best_reward = agent_reward
        return best_action
    
    def reward(self, planning_state):
        """
        simple reward based on distance from goal, distance from other collidable objects, and for keeping up speed
        """
        
        agent_x,agent_y = planning_state.dynamic_objects[self.agent_num].x, planning_state.dynamic_objects[self.agent_num].y
        dist_reward = -.5*np.sqrt((agent_x-self.goal_pos[0])**2 + (agent_y-self.goal_pos[1])**2)
        collision_avoidance_reward = 0
        for i in range(len(planning_state.dynamic_objects)):
            if i != self.agent_num:
                if planning_state.dynamic_objects[self.agent_num].intersect(planning_state.dynamic_objects[i]):
                    collision_avoidance_reward = -1000000 # massive penalty
                else:
                    other_x,other_y = planning_state.dynamic_objects[i].x, planning_state.dynamic_objects[i].y
                    collision_avoidance_reward += 500*min(np.sqrt((agent_x-other_x)**2 + (agent_y-other_y)**2),300)
        speed_reward = -15*(planning_state.dynamic_objects[self.agent_num].vel-10)**2       
            
        return dist_reward+collision_avoidance_reward+speed_reward
        
