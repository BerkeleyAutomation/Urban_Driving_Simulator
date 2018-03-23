from gym_urbandriving.agents.pursuit_agent import PursuitAgent
from gym_urbandriving.assets import Car, TrafficLight, CrosswalkLight, Pedestrian
from gym_urbandriving.agents import NullAgent, TrafficLightAgent, CrosswalkLightAgent, PursuitAgent
from copy import deepcopy
import gym_urbandriving as uds

class VelocityMPCPlanner:
    def __init__(self, lookahead=10):
        self.lookahead = lookahead


    def plan(self, state, agent_num):
        agents = []
        for i,obj in enumerate(state.dynamic_objects):
            if type(obj) in {Car, Pedestrian}:
                agents.append(PursuitAgent(i))
            elif type(obj) in {TrafficLight}:
                agents.append(NullAgent(i))
            elif type(obj) in {CrosswalkLight}:
                agents.append(CrosswalkLightAgent(i))
            else:
                agents.append(NullAgent(i))

        state_copy = deepcopy(state)
        testing_env = uds.UrbanDrivingEnv(init_state=state_copy,
                                  visualizer=None,
                                  max_time=500,
                                  randomize=False,
                                  agent_mappings={Car:NullAgent,
                                                  TrafficLight:NullAgent},
        )
        state_copy = testing_env.current_state
        if state_copy.dynamic_objects[agent_num].trajectory.stopped:
            state_copy.dynamic_objects[agent_num].trajectory.set_vel(4)
            for t in range(self.lookahead):
                actions = []
                for agent in agents:
                    action = agent.eval_policy(state_copy)
                    actions.append(action)
                state_copy, reward, done, info_dict = testing_env._step_test(actions)
                done = state_copy.collides_any_dynamic(agent_num)
                if done:
                    break
            if not done:
                return 4
            return 0

        elif not state_copy.dynamic_objects[agent_num].trajectory.stopped:
            for t in range(self.lookahead):
                actions = []
                for agent in agents:
                    action = agent.eval_policy(state_copy)
                    actions.append(action)
                state_copy, reward, done, info_dict = testing_env._step_test(actions)
                done = state_copy.collides_any_dynamic(agent_num)
                if done:
                    break
            if done:
                return 0
            return 4
