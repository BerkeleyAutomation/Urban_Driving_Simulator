import numpy as np
from functools import partial
from ompl import util as ou
from ompl import base as ob
from ompl import control as oc
from ompl import geometric as og
from scipy.integrate import odeint


class RRTMAgent:
    def __init__(self, goal_state,agent_num=0):
        self.agent_num = agent_num
        self.goal_state = goal_state
        self.idx = 0

    
    def add_plan(self,plan):

        self.plan = plan

    def eval_policy(self,state):

        action = self.plan[self.idx]

        self.idx += 1
        # print "AGENT NUMBER ",self.agent_num
        # print "ACTION ", action
        return action

    def is_done(self):

        if self.idx == len(self.plan):
            return True
        else:
            return False
            
