import numpy as np
from gym_urbandriving.utils.PID import PIDController
from gym_urbandriving.agents.pursuit_agent import PursuitAgent
from gym_urbandriving.assets import Car, TrafficLight
from gym_urbandriving.agents import NullAgent, TrafficLightAgent, PursuitAgent
from copy import deepcopy
import gym_urbandriving as uds

class PlanningPursuitAgent(PursuitAgent):
    """
    Agent which uses PID to implement a pursuit control policy
    Uses a trajectory with x,y,v,-

    Attributes
    ----------
    agent_num : int
        Index of this agent in the world.
        Used to access its object in state.dynamic_objects
    """
        
    def eval_policy(self, state):
        """
        Returns action based next state in trajectory. 

        Parameters
        ----------
        state : PositionState
            State of the world, unused

        Returns
        -------
        action
            Keyboard action
        """
        agents = []
        for i,obj in enumerate(state.dynamic_objects):
            if type(obj) in {Car}:
                agents.append(PursuitAgent(i))
            elif type(obj) in {TrafficLight}:
                agents.append(TrafficLightAgent(i))
            else:
                agents.append(NullAgent(i))

        state_copy = deepcopy(state)
        testing_env = uds.UrbanDrivingEnv(init_state=state_copy,
                                  visualizer=None,
                                  max_time=500,
                                  randomize=False,
                                  agent_mappings={Car:NullAgent,
                                                  TrafficLight:TrafficLightAgent},
                                  use_ray=False
        )
        state_copy = testing_env.current_state
        if state_copy.dynamic_objects[self.agent_num].trajectory.stopped:
            state_copy.dynamic_objects[self.agent_num].trajectory.restart()
            for t in range(10):
                actions = []
                for agent in agents:
                    action = agent.eval_policy(state_copy)
                    actions.append(action)
                state_copy, reward, done, info_dict = testing_env._step_test(actions)
                done = state_copy.collides_any(self.agent_num)
                if done:
                    break
            if not done:
                state.dynamic_objects[self.agent_num].trajectory.restart()

        elif not state_copy.dynamic_objects[self.agent_num].trajectory.stopped:
            for t in range(10):
                actions = []
                for agent in agents:
                    action = agent.eval_policy(state_copy)
                    actions.append(action)
                state_copy, reward, done, info_dict = testing_env._step_test(actions)
                done = state_copy.collides_any(self.agent_num)
                if done:
                    break
            if done:
                state.dynamic_objects[self.agent_num].trajectory.modify_to_stop()

        return super(PlanningPursuitAgent, self).eval_policy(state)


