class Action(object):
    def get_action(self):
        raise NotImplementedError

class SteeringAction(Action):
    def __init__(self, steer, acc):
        self.steer = steer
        self.acc = acc
    def get_action(self):
        return self.steer, self.acc

class VelocityAction(Action):
    def __init__(self, vel):
        self.vel = vel
    def get_action(self):
        return self.vel

class LastValidAction(Action):
    def __init__(self):
        pass
