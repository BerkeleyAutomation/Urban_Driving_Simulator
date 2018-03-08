import numpy as np

class ControlAgent:
    """
    Agent which follows a control trajectory. 

    Attributes
    ----------
    agent_num : int
        Index of this agent in the world.
        Used to access its object in state.dynamic_objects
    """
    def __init__(self, agent_num=0):
        self.agent_num = agent_num
        
    def eval_policy(self, state):
        obj = state.dynamic_objects[self.agent_num]
        traj = obj.trajectory
        
        if not 'cs' == traj.mode:
            raise ValueError()

        if traj is None or traj.is_empty():
            return None
        else:
            return traj.pop()