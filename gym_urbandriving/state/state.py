import gym
from copy import deepcopy
import numpy as np

class PositionState:
    static_objects = []
    def __init__(self):
        self.dimensions = (1000, 1000)
        self.dynamic_objects = []
        self.dynamic_collisions = None
        self.static_collisions = None
        return

    def get_collisions(self):
        if (self.dynamic_collisions is not None and
            self.static_collisions is not None):
            return self.dynamic_collisions, self.static_collisions
        self.dynamic_collisions = []
        self.static_collisions = []
        for i, dobj in enumerate(self.dynamic_objects):
            for j, sobj in enumerate(self.static_objects):
                if dobj.collides(sobj):
                    self.static_collisions.append({i, j})
            for j in range(i, len(self.dynamic_objects)):
                dobj1 = self.dynamic_objects[j]
                if j > i and dobj.collides(dobj1):
                    self.dynamic_collisions.append({i, j})
        return self.dynamic_collisions, self.static_collisions

    def collides_any(self, agent_num=0):
        if (self.dynamic_collisions is None or
            self.static_collisions is None):
            self.get_collisions()
            
        return any([agent_num in pair for pair in self.dynamic_collisions +
                    self.static_collisions])

    def reset_collisions(self):
        self.dynamic_collisions = None
        self.static_collisions = None

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if (k == "static_objects"):
                setattr(result, k, v)
            elif (k in {"dynamic_collisions", "static_collisions"}):
                setattr(result, k, None)
            else:
                setattr(result, k, deepcopy(v, memo))
        return result

    # TODO: fix this to get a better featurization
    def vectorize_state(self):      
        state_vec = []
        for obj in self.dynamic_objects:
            state_vec.extend([(obj.x-500)/500, (obj.y-500)/500, (obj.vel-10)/10])
        return state_vec
    
