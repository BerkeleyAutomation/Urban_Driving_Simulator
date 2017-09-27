import gym
from copy import deepcopy

class PositionState:
    def __init__(self):
        self.dimensions = (1000, 1000)
        self.dynamic_objects = []
        self.static_objects = []
        return

    def done(self):
        """
        returns true if collisions are present
        TODO: have this call collides_any
        """
        for i, dobj in enumerate(self.dynamic_objects):
            for j, sobj in enumerate(self.static_objects):
                if dobj.collides(sobj):
                    return True
            for j, dobj1 in enumerate(self.dynamic_objects[i+1:]):
                if dobj.collides(dobj1):
                    return True
        return False

    def collides_any(self, obj_id):
        """
        checks for any collisions for a specified object
        """
        dobj = self.dynamic_objects[obj_id]
        for j, sobj in enumerate(self.static_objects):
            if dobj.collides(sobj):
                return True
        for j, dobj1 in enumerate(self.dynamic_objects):
            if j is not obj_id and dobj.collides(dobj1):
                return True
        return False
