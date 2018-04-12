class PedestrianAgent(object):
    """
    Supervisor Agent for controlling pedestrians
    
    Attributes
    ----------
    agent_num : int
        Index of this agent in the world
    """
    def __init__(self, agent_num=0):
        self.agent_num = agent_num
    def eval_policy(self, state):
        """
        Returns action based on state of world
        
        Parameters
        ----------
        state : PositionState
            State of the world

        Returns
        -------
        Turning angle, acceleration pair
        """
        if (state.collides_any(self.agent_num, "pedestrians")):
            ped = state.dynamic_objects['pedestrians'][str(self.agent_num)]
            vel = -ped.vel
            return 0, vel
        return 0, 1
