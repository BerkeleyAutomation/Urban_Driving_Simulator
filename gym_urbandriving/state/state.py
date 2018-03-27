import gym
from copy import deepcopy
import numpy as np
from gym_urbandriving.assets import TrafficLight

class PositionState:
    """
    Abstract class representing the objects in a scene
    """
    static_objects = []
    def __init__(self, data, car_model="kinematic"):
        self.dimensions = (1000, 1000)
        self.dynamic_objects = {}
        self.time = 0

        self.agent_config = data['agents']

        assert (car_model in {"kinematic", "point", "reeds_shepp"})
        self.car_model = car_model
        self.randomize()
        return

    def randomize(self):
        """
        Not implemented. Override this in custom states"
        """
        pass

    def get_collisions(self):
        """
        Get list of all collisions in this state

        Returns
        -------
        list
            List of tuples, where each tuple contains a pair of coliding object indices. Dynamic_collisions contains collisions between cars and other cars.
        list
            The corresponding list for collisions between dynamic objects and static objects
        """
        dynamic_collisions, static_collisions = [], []

        for key in self.dynamic_objects.keys():
            for i, dobj in self.dynamic_objects[key].items():
                i = int(i)
                for j, sobj in enumerate(self.static_objects):
                    if dobj.collides(sobj):
                        static_collisions.append([i, j,key])

                for j in range(i, len(self.dynamic_objects[key])):
                    dobj1 = self.dynamic_objects[key][str(j)]
                    if j > i and dobj.collides(dobj1):
                        dynamic_collisions.append([i, j,key])

        return dynamic_collisions, static_collisions


    def collides_any(self, agentnum,type_of_agent = 'background_cars'):
        """
        Returns if the agentnum object in the scene is colliding with any other object

        Parameters
        ----------
        agentnum : int
            The index of the object to query

        Returns
        -------
        bool
            True if this object is colliding
        """
        dynamic_collisions, static_collisions = self.get_collisions()
        for coll in dynamic_collisions:
            if (agentnum in coll) and (type_of_agent in coll):
                return True
        for coll in static_collisions:
            if (agentnum in coll) and (type_of_agent in coll):
                return True
        return False
    
    def collides_any_dynamic(self, agentnum,type_of_agent = 'background_cars'):
        dynamic_collisions, static_collisions = self.get_collisions()
        for coll in dynamic_collisions:
            if (agentnum in coll) and (type_of_agent in coll):
                return True
        return False

    def min_dist_to_coll(self, agentnum,type_of_agent = 'background_cars'):
        """
        Returns the minimum distance between the object with id agentnum and a collideable object.

        Parameters
        ----------
        agentnum : int
            The index of the object to query

        Returns
        -------
        float
            Distance to nearest collideable object
        """
        min_dist = np.finfo('f').max
        obj = self.dynamic_objects[type_of_agent][agentnum]
        for j, sobj in enumerate(self.static_objects):
            if obj.can_collide(sobj):
                min_dist = min(min_dist, obj.dist_to(sobj))

        for key in self.dynamic_objects.keys():
            for j, dobj in enumerate(self.dynamic_objects):
                if j != agentnum and obj.can_collide(dobj):
                    min_dist = min(min_dist, obj.dist_to(dobj))
        return min_dist
