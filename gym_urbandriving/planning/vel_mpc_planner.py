from copy import deepcopy
import gym_urbandriving as uds
from gym_urbandriving.actions import VelocityAction
import IPython

class VelocityMPCPlanner:
    def __init__(self, lookahead=10):
        self.lookahead = lookahead


    def plan(self, state, agent_num,type_of_agent = "background_cars"):
        
        state_copy = deepcopy(state)
        testing_env = uds.UrbanDrivingEnv(init_state=state_copy,
                                          randomize=False)

        num_controlled_cars = state_copy.agent_config["controlled_cars"]
        empty_actions = [None]*num_controlled_cars

        state_copy = testing_env.current_state
        if state_copy.dynamic_objects[type_of_agent][str(agent_num)].trajectory.stopped:
            
            state_copy.dynamic_objects[type_of_agent][str(agent_num)].trajectory.set_vel(VelocityAction(4.0))
            for t in range(self.lookahead):
                
                state_copy, reward, done, info_dict = testing_env._step(empty_actions,background_simplified = True)
                state_copy = state_copy[0]
                done = state_copy.collides_any_dynamic(agent_num,type_of_agent = type_of_agent)
                if done:
                    break
            if done:
                return VelocityAction(0.0)
            return VelocityAction(4.0)


        elif not state_copy.dynamic_objects[type_of_agent][str(agent_num)].trajectory.stopped:
            for t in range(self.lookahead):
                state_copy, reward, done, info_dict = testing_env._step(empty_actions,background_simplified = True)
                state_copy = state_copy[0]
                done = state_copy.collides_any_dynamic(agent_num,type_of_agent = type_of_agent)
                if done:
                    break
            if done:
                return VelocityAction(0.0)
            return VelocityAction(4.0)

