from gym_urbandriving.assets.traffic_light import TrafficLight
import numpy as np
import shapely
import os
import gym_urbandriving as uds
from gym_urbandriving.assets import Terrain, Lane, Street, Sidewalk,\
    Pedestrian, Car, TrafficLight

import os



LIGHT_ARC = np.pi / 16
LIGHT_DISTANCE = 300

def distance(p1, p2):
    return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5

class Featurizer(object):
    """
    Object to convert a state observation into a Q-LIDAR observation.

    Attributes
    ----------
    beam_distance : int
        How far each "LIDAR" beam will project into the scene
    n_arcs :
        How many "LIDAR" beams to project around the car
    """
    def __init__(self, beam_distance=300, n_arcs=9):

        self.arc_deltas = np.arange(n_arcs + 1) / (float(n_arcs) / 2) - 1
        self.arc_deltas = [i*np.pi/2 for i in self.arc_deltas]
        self.beam_distance = beam_distance
        pass


    def featurize(self, current_state, controlled_key):
        """
        Returns a Numpy array of a Q-LIDAR representation of the state
        
        Parameters
        ----------
        current_state : PositionState
            State of the world
        controlled_key : 
            Key for controlled car in the state to generate a feature for

        Returns
        -------
        Numpy array. For each ray projected into the scene, adds distance \
        to collision, angle to collision, and velocity of intersected object
        """
        car = current_state.dynamic_objects['controlled_cars'][controlled_key]

        x, y, angle, vel = car.get_state()

        min_light_d = LIGHT_DISTANCE
        min_light_state = None

        light_cone = shapely.geometry.Polygon([(x, y),
                                               (x + np.cos(-LIGHT_ARC+angle)*LIGHT_DISTANCE,
                                                y - np.sin(-LIGHT_ARC+angle)*LIGHT_DISTANCE),
                                               (x + np.cos(LIGHT_ARC+angle)*LIGHT_DISTANCE,
                                                y - np.sin(LIGHT_ARC+angle)*LIGHT_DISTANCE),])



        #print(goal_d, goal_a)
        features = [vel]
        #print(goalx, goaly)

        for arc_delta in self.arc_deltas:
            arc_angle = angle + arc_delta
            xd = x + np.cos(arc_angle)*self.beam_distance
            yd = y - np.sin(arc_angle)*self.beam_distance
            linestring = shapely.geometry.LineString([(x, y), (xd, yd)])
            min_coll_d = self.beam_distance
            min_coll_type = None
            min_coll_vel = 0
            min_coll_angle = 0
            #min_coll_acc = 0
            #min_coll_ang_vel = 0


            for sobj in current_state.static_objects:
                if car.can_collide(sobj) and linestring.intersects(sobj.get_shapely_obj()):
                    isect = list(linestring.intersection(sobj.get_shapely_obj()).coords)[0]
                    d = distance((x, y), isect)
                    if (d < min_coll_d):
                        min_coll_d = d
                        min_coll_type = type(sobj)
                        min_coll_vel = 0
                        min_coll_angle = 0
                        #min_coll_acc = 0
                        #min_coll_ang_vel = 0
            for did, dobj in enumerate(current_state.dynamic_objects):
                if car is not dobj and car.can_collide(dobj) \
                   and type(dobj) is not TrafficLight and linestring.intersects(dobj.get_shapely_obj()):
                    isect = list(linestring.intersection(dobj.get_shapely_obj()).coords)[0]
                    d = distance((x, y), isect)
                    if (d < min_coll_d):
                        min_coll_d = d
                        min_coll_type = type(dobj)
                        min_coll_vel = dobj.vel
                        min_coll_angle = (angle - dobj.angle) % (2 * np.pi)


            #print(min_coll_d, min_coll_type, 180 * min_coll_angle / np.pi, min_coll_vel)
            features.extend([min_coll_d, np.sin(min_coll_angle), np.cos(min_coll_angle), min_coll_vel])
        for dobj in current_state.dynamic_objects:
            if type(dobj) is TrafficLight and light_cone.intersects(dobj.get_shapely_obj()):
                if np.abs((dobj.angle + np.pi) % (2 * np.pi) - angle) < np.pi / 4:
                    
                    d = distance((x, y), (dobj.x, dobj.y))
                    if (d < min_light_d):
                        min_light_d = d
                        min_light_state = dobj.color
        features.extend([min_light_d, {'red':1,'yellow':0.5,'green':0, None:-1}[min_light_state]])
        #print(min_light_d, min_light_state)
        #print(x, y, vel)
#        print(features)
        #print(len(features))
        return features
