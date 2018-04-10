class PedestrianAgent(object):
    def __init__(self, agent_num=0):
        self.agent_num = agent_num
    def eval_policy(self, state):
        if (state.collides_any(self.agent_num, "pedestrians")):
            return 0, -1
        return 0, 1
