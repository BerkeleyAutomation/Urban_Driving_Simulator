import ray

@ray.remote
class NullAgent:
    def __init__(self, agent_num=0):
        return
    def eval_policy(self, state):
        assert(False)
        return None

