from copy import deepcopy
import gym_urbandriving as uds
from gym_urbandriving.actions import VelocityAction
import IPython

class VelocityCSPPlanner:
    def __init__(self, lookahead=10):
        self.lookahead = lookahead


    def plan(self, state, agent_num,type_of_agent = "background_cars"):
        
        state_copy = deepcopy(state)
        testing_env = uds.UrbanDrivingEnv(init_state=state_copy,
                                          randomize=False)

       ####MAKE BLOB DICT#### 

       ###SOLVE FOR CSP
