import numpy as np
import json
import os
from six import iteritems
import random
import pygame
import hashlib

from fluids.consts import *
from fluids.assets import *
from fluids.utils import *
from fluids.version import __version__


basedir = os.path.dirname(__file__)

id_index = 0
def get_id():
    global id_index
    r = id_index
    id_index = id_index + 1
    return r


class State(object):
    """
    This class represents the state of the world

    Parameters
    ----------
    layout: str
        Name of json layout file specifiying environment object positions. Default is "fluids_state_city"
    controlled_cars: int
        Number of cars to accept external control for
    background_cars: int
        Number of cars to control with the background planner
    background_peds: int
        Number of pedestrians to control with the background planner
    """
    def __init__(self,
                 layout          =STATE_CITY,
                 controlled_cars =0,
                 background_cars =0,
                 background_peds =0,
                 vis_level       =1):

        fluids_print("Loading layout: " + layout)
        cfilename = layout + __version__ + ".json"
        layout = open(os.path.join(basedir, "layouts", layout + ".json"))
        cached_layout = lookup_cache(cfilename)
        cache_found = cached_layout is not False
        if cached_layout:
            fluids_print("Cached layout found")
            layout = cached_layout

        layout = json.load(layout)

        
        self.time             = 0
        self.objects          = {}
        self.type_map         = {k:{} for k in [Terrain, Lane, Street, CrossWalk, Sidewalk,
                                                TrafficLight, Car, CrossWalkLight, Pedestrian, PedCrossing]}
        self.static_objects   = {}
        self.dynamic_objects  = {}
        self.dimensions       = (layout['dimension_x'] + 800, layout['dimension_y'])
        self.vis_level        = vis_level


        lanes = []
        sidewalks = []
        fluids_print("Creating objects")
        for obj_info in layout['static_objects']:
            typ = {"Terrain"    : Terrain,
                   "Lane"       : Lane,
                   "Street"     : Street,
                   "CrossWalk"  : CrossWalk,
                   "PedCrossing": PedCrossing,
                   "Sidewalk"   : Sidewalk}[obj_info['type']]

            obj = typ(state=self, vis_level=vis_level, **obj_info)

            if typ == Lane:
                lanes.append(obj)
            if typ == Sidewalk:
                sidewalks.append(obj)
            key = get_id()
            self.type_map[typ][key] = obj
            self.objects[key] = obj
            self.static_objects[key] = obj

        car_ids = []
        for obj_info in layout['dynamic_objects']:
            typ = {"Car"           : Car,
                   "TrafficLight"  : TrafficLight,
                   "CrossWalkLight": CrossWalkLight,
                   "Pedestrian"    : Pedestrian}[obj_info['type']]

            obj = typ(state=self, vis_level=vis_level, **obj_info)

            key = get_id()
            if type == Car:
                car_ids.append(key)
            self.type_map[typ][key] = obj
            self.objects[key] = obj
            self.dynamic_objects[key] = obj


        fluids_print("Generating trajectory map")
        if 'waypoints' in layout:
            wp_map = {}
            self.waypoints = []
            self.ped_waypoints = []

            for wp_info in layout['waypoints']:
                index = wp_info.pop('index')
                wp = Waypoint(**wp_info)
                wp_map[index] = wp
                self.waypoints.append(wp)
            for wp in self.waypoints:
                wp.nxt = [wp_map[index] for index in wp.nxt]

            wp_map = {}
            for wp_info in layout['ped_waypoints']:
                index = wp_info.pop('index')
                wp = Waypoint(**wp_info)
                wp_map[index] = wp
                self.ped_waypoints.append(wp)
            for wp in self.ped_waypoints:
                wp.nxt = [wp_map[index] for index in wp.nxt]
        else:
            self.generate_waypoints_init()
        
            layout['waypoints'] = []
            layout['ped_waypoints'] = []
            for wp in self.waypoints:
                wpdict = {"index":wp.index, "x":wp.x, "y": wp.y, "angle":wp.angle,
                          "nxt":[w.index for w in wp.nxt]}
                layout['waypoints'].append(wpdict)
            for wp in self.ped_waypoints:
                wpdict = {"index":wp.index, "x":wp.x, "y": wp.y, "angle":wp.angle,
                          "nxt":[w.index for w in wp.nxt]}
                layout['ped_waypoints'].append(wpdict)

        fluids_print("Generating cars")
        for i in range(controlled_cars + background_cars):
            while True:
                start = lanes[np.random.random_integers(0, len(lanes)-1)]
                x = np.random.uniform(start.minx + 50, start.maxx - 50)
                y = np.random.uniform(start.miny + 50, start.maxy - 50)
                angle = start.angle + np.random.uniform(-0.1, 0.1)
                car = Car(state=self, x=x, y=y, angle=angle, vis_level=vis_level)
                min_d = min([car.dist_to(other) for k, other in iteritems(self.type_map[Car])] + [np.inf])
                if min_d > 10 and not self.is_in_collision(car):
                    key = get_id()
                    for waypoint in self.waypoints:
                        if car.intersects(waypoint):
                            while car.intersects(waypoint):
                                waypoint = random.choice(waypoint.nxt)
                            waypoint = random.choice(waypoint.nxt)
                            car.waypoints = [waypoint]
                            break
                    self.type_map[Car][key] = car
                    self.objects[key] = car
                    car_ids.append(key)
                    self.dynamic_objects[key] = car
                    break

        self.controlled_cars = {k: self.objects[k] for k in car_ids[:controlled_cars]}
        for k, car in iteritems(self.controlled_cars):
            car.color = (5, 250, 0)
        self.background_cars = {k: self.objects[k] for k in car_ids[controlled_cars:]}


        fluids_print("Generating peds")
        for i in range(background_peds):
            while True:
                wp = random.choice(self.ped_waypoints)
                ped = Pedestrian(state=self, x=wp.x, y=wp.y, angle=wp.angle, vis_level=vis_level)
                while ped.intersects(wp):
                    wp = random.choice(wp.nxt)
                ped.waypoints = [wp]
                if not self.is_in_collision(ped):
                    key = get_id()
                    self.objects[key] = ped
                    self.type_map[Pedestrian][key] = ped
                    self.dynamic_objects[key] = obj
                    break


        if not cache_found:
            fluids_print("Caching layout to: " + cfilename)
            with open(get_cache_filename(cfilename), "w") as outfile:
                json.dump(layout, outfile, indent=1)
        fluids_print("State creation complete")
        if vis_level:
            self.static_surface       = pygame.Surface(self.dimensions)
            try:
                self.static_debug_surface = pygame.Surface(self.dimensions, pygame.SRCALPHA)
            except ValueError:
                fluids_print("WARNING: Alpha channel not available. Visualization may be slow")
                self.static_debug_surface = self.static_surface.copy()
            for k, obj in iteritems(self.static_objects):
                if type(obj) != CrossWalk:
                    obj.render(self.static_surface)
                else:
                    obj.render(self.static_debug_surface)
            for waypoint in self.waypoints:
                waypoint.render(self.static_debug_surface)
            for waypoint in self.ped_waypoints:
                waypoint.render(self.static_debug_surface, color=(255, 255, 0))

    def generate_waypoints_init(self):
        self.waypoints      = [lane.start_waypoint for k, lane in iteritems(self.type_map[Lane])]
        self.waypoints.extend([lane.end_waypoint   for k, lane in iteritems(self.type_map[Lane])])

        for k, street in iteritems(self.type_map[Street]):
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
            new_waypoints.extend(waypoint.smoothen(smooth_level=2000))
        self.waypoints.extend(new_waypoints)

        self.ped_waypoints = []
        for k, obj in iteritems(self.objects):
            if type(obj) in {CrossWalk, Sidewalk}:
                self.ped_waypoints.extend(obj.start_waypoints)
                self.ped_waypoints.extend(obj.end_waypoints)
        for k, cross in iteritems(self.type_map[PedCrossing]):
            for waypoint in self.ped_waypoints:
                if cross.intersects(waypoint):
                    test_point = (waypoint.x + np.cos(waypoint.angle),
                                  waypoint.y - np.sin(waypoint.angle))
                    if cross.contains_point(test_point):
                        cross.in_waypoints.append(waypoint)
                    else:
                        cross.out_waypoints.append(waypoint)
            for in_p in cross.in_waypoints:
                for out_p in cross.out_waypoints:
                    dangle = (in_p.angle - out_p.angle) % (2 * np.pi)
                    if dangle < 0.75*np.pi or dangle > 1.25*np.pi:
                        in_p.nxt.append(out_p)

        new_waypoints = []
        for waypoint in self.ped_waypoints:
            new_waypoints.extend(waypoint.smoothen(smooth_level=1500))
        self.ped_waypoints.extend(new_waypoints)

        i = 0
        for wp in self.waypoints:
            wp.index = i
            i += 1
        for wp in self.ped_waypoints:
            wp.index = i
            i += 1

    def get_static_surface(self):
        return self.static_surface

    def get_static_debug_surface(self):
        return self.static_debug_surface

    def get_dynamic_surface(self):
        try:
            dynamic_surface = pygame.Surface(self.dimensions, pygame.SRCALPHA)
        except ValueError:
            dynamic_surface = self.static_debug_surface.copy()
        for typ in [Pedestrian, TrafficLight, CrossWalkLight]:
            for k, obj in iteritems(self.type_map[typ]):
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
                for k, other in iteritems(self.type_map[ctype]):
                    if obj.collides(other):
                        return True
        return False

    def min_distance_to_collision(self, obj):
        collideables = obj.collideables
        mind = 0
        for ctype in collideables:
            for k, other in iteritems(self.type_map[ctype]):
                d = obj.dist_to(other)
                if d < mind:
                    mind = d
        return mind

    def update_vis_level(self, new_vis_level):
        self.vis_level = new_vis_level
        for k, obj in iteritems(self.objects):
            obj.vis_level = new_vis_level


    def get_controlled_collisions(self):
        return
