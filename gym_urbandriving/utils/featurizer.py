from gym_urbandriving.assets.traffic_light import TrafficLight
import numpy as np
import shapely
import os
import gym_urbandriving as uds
import os


N_ARCS = 9
ARC_DELTAS = [-1, -0.5, -0.25, -0.15, -0.1, 0, 0.1, 0.15, 0.25, 0.5, 1]
ARC_DELTAS = [i*np.pi/2 for i in ARC_DELTAS]
BEAM_DISTANCE = 300
LIGHT_ARC = np.pi / 16
LIGHT_DISTANCE = 300

def distance(p1, p2):
    return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5

class Featurizer(object):
    def __init__(self):
        pass

    def featurize(self, current_state, controlled_key):

        car = current_state.dynamic_objects['controlled_cars'][controlled_key]

        x, y, angle, vel = car.get_state()

        min_light_d = LIGHT_DISTANCE
        min_light_state = 0

        light_cone = shapely.geometry.Polygon([(x, y),
                                               (x + np.cos(-LIGHT_ARC+angle)*LIGHT_DISTANCE,
                                                y - np.sin(-LIGHT_ARC+angle)*LIGHT_DISTANCE),
                                               (x + np.cos(LIGHT_ARC+angle)*LIGHT_DISTANCE,
                                                y - np.sin(LIGHT_ARC+angle)*LIGHT_DISTANCE),])



        #print(goal_d, goal_a)
        features = [vel]
        #print(goalx, goaly)

        for arc_delta in ARC_DELTAS:
            arc_angle = angle + arc_delta
            xd = x + np.cos(arc_angle)*BEAM_DISTANCE
            yd = y - np.sin(arc_angle)*BEAM_DISTANCE
            linestring = shapely.geometry.LineString([(x, y), (xd, yd)])
            min_coll_d = BEAM_DISTANCE
            min_coll_type = None
            min_coll_vel = 0
            min_coll_angle = 0
            min_coll_acc = 0
            min_coll_ang_vel = 0


            for sobj in current_state.static_objects:
                if car.can_collide(sobj) and linestring.intersects(sobj.get_shapely_obj()):
                    isect = list(linestring.intersection(sobj.get_shapely_obj()).coords)[0]
                    d = distance((x, y), isect)
                    if (d < min_coll_d):
                        min_coll_d = d
                        min_coll_type = type(sobj)
                        min_coll_vel = 0
                        min_coll_angle = 0
                        min_coll_acc = 0
                        min_coll_ang_vel = 0
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
                d = distance((x, y), (dobj.x, dobj.y))
                if (d < min_light_d):
                    min_light_d = d
                    min_light_state = dobj.color
        features.extend([min_light_d, min_light_state])
        #print(min_light_d, min_light_state)
        #print(x, y, vel)
#        print(features)
        #print(len(features))
        return features
