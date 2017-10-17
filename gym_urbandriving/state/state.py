import gym
from copy import deepcopy
import numpy as np

class PositionState:
    static_objects = []
    def __init__(self):
        self.dimensions = (1000, 1000)
        self.dynamic_objects = []
        return

    def get_collisions(self):
        dynamic_collisions = []
        static_collisions = []

