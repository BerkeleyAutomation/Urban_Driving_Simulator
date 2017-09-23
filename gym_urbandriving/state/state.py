import gym
from copy import deepcopy

class PositionState:
    def __init__(self):
        self.dimensions = (1000, 1000)
        self.dynamic_objects = []
        self.terrain_objects = []
        self.street_objects = []
        return

    def __deepcopy__(self, memo):
        newstate = PositionState()
        newstate.dynamic_objects = deepcopy(self.dynamic_objects)
        newstate.terrain_objects = deepcopy(self.terrain_objects)
        newstate.street_objects = deepcopy(self.street_objects)
        return newstate

    def has_collisions(self):
        """Check for collisions"""
        return False

    def done(self):
        return False
    
    def get_static_objects(self):
        return self.terrain_objects + self.street_objects
    
    def get_dynamic_objects(self):
        return self.dynamic_objects
