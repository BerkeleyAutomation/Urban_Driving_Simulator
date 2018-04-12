class PedestrianAgent(object):
    def __init__(self, agent_num=0):
        self.agent_num = agent_num
    def eval_policy(self, state):
        if (state.collides_any(self.agent_num, "pedestrians")):
            ped = state.dynamic_objects['pedestrians'][str(self.agent_num)]
            vel = -ped.vel
            return 0, vel
        return 0, 1
