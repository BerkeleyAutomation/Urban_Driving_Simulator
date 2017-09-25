import gym
from copy import deepcopy

class PositionState:
    def __init__(self):
        self.dimensions = (1000, 1000)
        self.dynamic_objects = []
        self.static_objects = []
        return
