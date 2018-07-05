class Action(object):
    def get_action(self):
        raise NotImplementedError

class KeyboardAction(Action):
    """
    This action passes control to keyboard input
    """
    pass
    
class SteeringAction(Action):
    """
    This action provides both steering and acceleration control

    Parameters
    ----------
    steer: float
    acc: float
    """

    def __init__(self, steer, acc):
        self.steer = steer
        self.acc = acc
    def get_action(self):
        return self.steer, self.acc

class VelocityAction(Action):
    """
    This action provides a target velocity for the car to track

    Parameters
    ----------
    vel: float
    """
    def __init__(self, vel):
        self.vel = vel
    def get_action(self):
        return self.vel

class LastValidAction(Action):
    """
    This action causes car to replay its last valid action.
    This is useful when testing coarse planning methods.
    """
    def __init__(self):
        pass
