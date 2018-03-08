from copy import deepcopy
import numpy as np

class AccelAgent:
    """
    Simple greedy search agent. Chooses action which maximizes expected time
    to next collision

    Attributes
    ----------
    actions : list
        Set of actions to choose from
    agent_num : int
        Index of this agent in the world.
        Used to access its object in state.dynamic_objects
    planning_env : UrbanDrivingEnv
        World simulator used internally to plan
    """

    def __init__(self, agent_num=0):
        self.agent_num = agent_num
        self.valid_actions = [(0, 1), (3, .5), (-3, .5), (0, -1)]
        self.quantum = 4
        return

    def eval_policy(self, state, nsteps=8):
        """
        Chooses best action for this agent in the state.
        Looks forward nsteps to evaluate best action
        Parameters
        ----------
        state : PositionState
            State of the world,
            with this agent controlling state.dynamic_objects[self.agent_num]
        nsteps : int
            How many steps forward to look in planning
        Returns
        -------
        action
            Best action
        """

        best_action = None
        best_time = 0
        best_angle_offset = np.pi/2

        for action in self.valid_actions:
            state_copy = deepcopy(state)
            time = 0

            for i, dobj in enumerate(state_copy.dynamic_objects):
                if i != self.agent_num:
                    dobj.step((0, 0))
                else:
                    dobj.step(action)

            angle_offset = abs((state_copy.dynamic_objects[self.agent_num].angle-(np.pi/4))%(np.pi/2)-(np.pi/4))

            for z in range(nsteps//self.quantum):
                for y in range(self.quantum):
                    for i, dobj in enumerate(state_copy.dynamic_objects):
                        if i != self.agent_num:
                            dobj.step((0, 0))
                        else:
                            dobj.step(action)

                time += 1
                if (state_copy.collides_any(self.agent_num)):
                    break

            if time > best_time or (time == best_time and angle_offset < best_angle_offset):
                best_action = action
                best_time = time
                best_angle_offset = angle_offset
  
        return best_action
