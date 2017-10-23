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
        dynamic_collisions, static_collisions = [], []
        for i, dobj in enumerate(self.dynamic_objects):
            for j, sobj in enumerate(self.static_objects):
                if dobj.collides(sobj):
                    static_collisions.append([i, j])
            for j in range(i, len(self.dynamic_objects)):
                dobj1 = self.dynamic_objects[j]
                if j > i and dobj.collides(dobj1):
                    dynamic_collisions.append([i, j])
        return dynamic_collisions, static_collisions


    def collides_any(self, agentnum):
        dynamic_collisions, static_collisions = self.get_collisions()
        for coll in dynamic_collisions:
            if agentnum in coll:
                return True
        for coll in static_collisions:
            if agentnum == coll[0]:
                return True
        return False

    def min_dist_to_coll(self, agentnum):
        min_dist = np.finfo('f').max
        obj = self.dynamic_objects[agentnum]
        for j, sobj in enumerate(self.static_objects):
            if obj.can_collide(sobj):
                min_dist = min(min_dist, obj.dist_to(sobj))
        for j, dobj in enumerate(self.dynamic_objects):
            if j != agentnum and obj.can_collide(dobj):
                min_dist = min(min_dist, obj.dist_to(dobj))
        return min_dist
