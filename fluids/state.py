import numpy as np
import json
import os
from six import iteritems
import random
import pygame

from fluids.consts import *
from fluids.assets import *


basedir = os.path.dirname(__file__)

id_index = 0
def get_id():
    global id_index
    r = id_index
    id_index = id_index + 1
    return r

class State(object):
    def __init__(self,
                 layout          =STATE_CITY,
                 controlled_cars =0,
                 control_space   =CTRL_STEERING,
                 background_cars =0,
                 background_peds =0,
                 vis_level       =1):


        layout = json.load(open(os.path.join(basedir, "layouts", layout + ".json")))
        self.time             = 0
        self.objects          = {}
        self.type_map         = {k:set() for k in [Terrain, Lane, Street, CrossWalk, Sidewalk,
                                           TrafficLight, Car, CrossWalkLight, Pedestrian]}
        self.static_objects   = {}
        self.dynamic_objects  = {}
        self.dimensions       = (layout['dimension_x'], layout['dimension_y'])
        self.vis_level        = vis_level
        
        lanes = []
        sidewalks = []
        for obj_info in layout['static_objects']:
            typ = {"Terrain"   : Terrain,
                   "Lane"      : Lane,
                   "Street"    : Street,
                   "CrossWalk" : CrossWalk,
                   "Sidewalk"  : Sidewalk}[obj_info.pop('type')]

            obj = typ(state=self, vis_level=vis_level, **obj_info)
            self.type_map[typ].add(obj)
            if typ == Lane:
                lanes.append(obj)
            if typ == Sidewalk:
                sidewalks.append(obj)
            key = get_id()
            self.objects[key] = obj
            self.static_objects[key] = obj

        car_ids = []
        for obj_info in layout['dynamic_objects']:
            typ = {"Car"           : Car,
                   "TrafficLight"  : TrafficLight,
                   "CrossWalkLight": CrossWalkLight,
                   "Pedestrian"    : Pedestrian}[obj_info.pop('type')]

            obj = typ(state=self, vis_level=vis_level, **obj_info)
            self.type_map[typ].add(obj)
            key = get_id()
            if type == Car:
                car_ids.append(key)
            self.objects[key] = obj
            self.dynamic_objects[key] = obj

        for i in range(controlled_cars + background_cars):
            while True:
                start = lanes[np.random.random_integers(0, len(lanes)-1)]
                x = np.random.uniform(start.minx + 50, start.maxx - 50)
                y = np.random.uniform(start.miny + 50, start.maxy - 50)
                angle = start.angle + np.random.uniform(-0.1, 0.1)
                car = Car(state=self, x=x, y=y, angle=angle, vis_level=vis_level)
                min_d = min([car.dist_to(other) for other in self.type_map[Car]] + [np.inf])
                if min_d > 10 and not self.is_in_collision(car):
                    key = get_id()
                    self.type_map[Car].add(car)
                    self.objects[key] = car
                    car_ids.append(key)
                    self.dynamic_objects[key] = car
                    break


        for i in range(background_peds):
            while True:
                start = sidewalks(np.random.random_integers(0, len(sidewalks)-1))
                x = np.random.uniform(start.minx + 50, start.maxx - 50)
                y = np.random.uniform(start.miny + 50, start.maxy - 50)
                angle = start.angle + np.random.uniform(-0.1, 0.1) + np.random.randint() * np.pi
                ped = Pedestrian(state=self, x=x, y=y, angle=angle, vis_level=vis_level)
                if not self.is_in_collision(ped):
                    key = get_id()
                    self.objects[key] = ped
                    self.type_map[Pedestrian].add(ped)
                    self.dynamic_objects[key] = obj
                    break

        self.controlled_cars = {k: self.objects[k] for k in car_ids[:controlled_cars]}
        for k, car in iteritems(self.controlled_cars):
            car.color = (155, 20, 20)
        self.background_cars = {k: self.objects[k] for k in car_ids[controlled_cars:]}

        self.waypoints      = [lane.start_waypoint for lane in self.type_map[Lane]]
        self.waypoints.extend([lane.end_waypoint for lane in self.type_map[Lane]])

        for street in self.type_map[Street]:
            for waypoint in self.waypoints:
                if street.intersects(waypoint):
                    test_point = (waypoint.x + np.cos(waypoint.angle),
                                  waypoint.y - np.sin(waypoint.angle))
                    if street.contains_point(test_point):
                        street.in_waypoints.append(waypoint)
                    else:
                        street.out_waypoints.append(waypoint)
            for in_p in street.in_waypoints:
                for out_p in street.out_waypoints:
                    dangle = (in_p.angle - out_p.angle) % (2 * np.pi)
                    if dangle < 0.75*np.pi or dangle > 1.25*np.pi:
                        in_p.nxt.append(out_p)

        new_waypoints = []
        for waypoint in self.waypoints:
            new_waypoints.extend(waypoint.smoothen())
        self.waypoints.extend(new_waypoints)
        for car in self.type_map[Car]:
            for waypoint in self.waypoints:
                if car.intersects(waypoint):
                    while car.intersects(waypoint):
                        waypoint = random.choice(waypoint.nxt)
                    waypoint = random.choice(waypoint.nxt)
                    car.waypoints = [waypoint]
                    break

                    

        if vis_level:
            self.static_surface = pygame.Surface(self.dimensions)
            for k, obj in iteritems(self.static_objects):
                obj.render(self.static_surface)
            if vis_level > 2:
                for waypoint in self.waypoints:
                    waypoint.render(self.static_surface)


    def get_static_surface(self):
        return self.static_surface

    def get_dynamic_surface(self):
        dynamic_surface = pygame.Surface(self.dimensions, pygame.SRCALPHA)
        for typ in [Pedestrian, TrafficLight, CrossWalkLight]:
            for obj in self.type_map[typ]:
                obj.render(dynamic_surface)
        for k, car in iteritems(self.background_cars):
            car.render(dynamic_surface)
        for k, car in iteritems(self.controlled_cars):
            car.render(dynamic_surface)
        if self.vis_level > 1:
            for kd, obj in iteritems(self.dynamic_objects):
                for ko, sobj in iteritems(self.objects):
                    if obj.collides(sobj):
                        pygame.draw.circle(dynamic_surface,
                                           (255, 0, 255),
                                           (int(obj.x), int(obj.y)),
                                           10)
        return dynamic_surface

    def is_in_collision(self, obj):
        collideables = obj.collideables
        for ctype in collideables:
            if ctype in self.type_map:
                for other in self.type_map[ctype]:
                    if obj.collides(other):
                        return True
        return False

    def min_distance_to_collision(self, obj):
        collideables = obj.collideables
        mind = 0
        for ctype in collideables:
            for other in self.type_map[ctype]:
                d = obj.dist_to(other)
                if d < mind:
                    mind = d
        return mind

    def get_controlled_collisions(self):
        return
