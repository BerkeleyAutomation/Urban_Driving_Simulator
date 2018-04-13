from gym_urbandriving.actions import SteeringAction

class Agent(object):
    """
    Base Class of agent. 
    """
    def __init__(self, agent_num=0):
        """
        Initializes the Agent Class

        Parameters
        ----------
        agent_num: int
            The number which specifies the agent in the dictionary

        """
        return

    def eval_policy(self, state, simplified=None):
        """
        Always returns the action (0, 0). 

        Parameters
        ----------
        state : PositionState
            State of the world, unused

        Returns
        -------
        SteeringAction(0, 0)
        """
        return SteeringAction(0, 0)

