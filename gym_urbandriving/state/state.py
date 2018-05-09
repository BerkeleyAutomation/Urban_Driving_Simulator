import gym
from copy import deepcopy
import numpy as np
from gym_urbandriving.assets import TrafficLight, Terrain, Street, Lane, Sidewalk, Car, CrosswalkLight, Pedestrian
from gym_urbandriving.agents import *
import json
import os
import random
import six

class PositionState:
    """
    Abstract class representing the objects in a scene
    """

    def __init__(self, data, car_model="kinematic"):
        self.dimensions = (1000, 1000)
        self.dynamic_objects = {}
        self.time = 0
        self.static_objects = []
        self.start_lanes = []
        self.goal_states = []
        self.agent_config = data['agents']
        self.dynamic_collisions, self.static_collisions, self.controlled_car_collisions = [], [], []
        self.last_coll = -1

        if 'state' in data['environment']:
            state_config = data['environment']['state']
            basedir = os.path.dirname(__file__)
            state_config = json.load(open(os.path.join(basedir, "configs/", state_config + ".json")))
        else:
            state_config = data['environment']['state_config']

        for obj_info in state_config['static_objects']:
            typ = {"Terrain":Terrain, "Lane":Lane, "Street":Street, "Sidewalk":Sidewalk}[obj_info.pop('type')]
            obj = typ(**obj_info)
            self.static_objects.append(obj)
        for obj_info in state_config['car_start_lanes']:
            self.start_lanes.append(Lane(**obj_info))

        self.state_config = state_config
        self.goal_states = state_config['goal_states']



        assert (car_model in {"kinematic", "point", "reeds_shepp"})
        self.car_model = car_model
        self.randomize()
        return

    def randomize(self):
        """
        Randomly generates car and pedestrian positions
        """
        self.dynamic_objects = {}
        self.dynamic_objects['controlled_cars'] = {}
        self.dynamic_objects['background_cars'] = {}
        self.dynamic_objects['pedestrians'] = {}
        self.dynamic_objects['traffic_lights'] = {}

        for car_index in range(self.agent_config['controlled_cars']):
            while True:
                start = np.random.random_integers(0, 3)
                lane = self.start_lanes[start]
                car = lane.generate_car(self.car_model)
                if not self.is_in_collision(car):
                    self.dynamic_objects['controlled_cars'][str(car_index)] = car
                    self.dynamic_objects['controlled_cars'][str(car_index)].destination = self.assign_goal_states(start)
                    break

        for car_index in range(self.agent_config['background_cars']):
            while True:
                start = np.random.random_integers(0, 3)
                lane = self.start_lanes[start]
                car = lane.generate_car(self.car_model)
                if not self.is_in_collision(car):
                    self.dynamic_objects['background_cars'][str(car_index)] = car
                    self.dynamic_objects['background_cars'][str(car_index)].destination = self.assign_goal_states(start)
                    break

        self.dynamic_objects['traffic_lights'] = {}
        if self.agent_config['use_traffic_lights']:

            for i, traffic_light in enumerate(self.state_config['traffic_lights']):
                self.dynamic_objects['traffic_lights'][str(i)] = TrafficLight(**traffic_light)
        self.dynamic_objects['crosswalk_lights'] = {}
        self.dynamic_objects['pedestrians'] = {}        
        if self.agent_config['use_pedestrians']:

            for i, crosswalk_light in enumerate(self.state_config['crosswalk_lights']):
                self.dynamic_objects['crosswalk_lights'][str(i)] = CrosswalkLight(**crosswalk_light)

            start_sidewalks = [s for s in self.static_objects if type(s) == Sidewalk]

            for ped_index in range(self.agent_config['number_of_pedestrians']):
                while True:
                    start = np.random.random_integers(0, len(start_sidewalks) - 1)
                    sidewalk = start_sidewalks[start]
                    ped = sidewalk.generate_man()
                    if not self.is_in_collision(ped):
                        self.dynamic_objects['pedestrians'][str(ped_index)] = ped
                        break
        #TODO Add pedestrians

        self.create_agents()

    def assign_goal_states(self, start_lane):
        """
        Assigns a random goal state to a car
        """
        goal_choices = deepcopy(self.goal_states)
        del goal_choices[start_lane]
        choice = random.choice(goal_choices)

        return [choice['x'], choice['y'], choice['vel'], np.deg2rad(choice['angle_deg'])]

    def create_agents(self):
        """
        Creates agents for objects in the scene
        """
        agent_mappings = {}
        for k, v in six.iteritems(self.agent_config['agent_mappings']):
            agent_mappings[{"Car":Car,
                            "TrafficLight":TrafficLight,
                            "CrosswalkLight":CrosswalkLight,
                            "Pedestrian":Pedestrian}[k]] = {"PlanningPursuitAgent":PlanningPursuitAgent,
                                                            "TrafficLightAgent":TrafficLightAgent,
                                                            "CrosswalkLightAgent":CrosswalkLightAgent,
                                                            "Agent": Agent,
                                                            "PedestrianAgent":PedestrianAgent,
                                                            "NeuralPursuitAgent":NeuralPursuitAgent}[v]

        self.bg_agents = {}
        for key in self.dynamic_objects.keys():
            if not key == 'controlled_cars':
                self.bg_agents[key] = []
                for i, index in enumerate(self.dynamic_objects[key]):
                    obj = self.dynamic_objects[key][index]
                    if type(obj) in agent_mappings:
                        self.bg_agents[key].append(agent_mappings[type(obj)](i))
        self.bg_agents['controlled_cars'] = []
        for i in range(self.agent_config['controlled_cars']):
            action_space = self.agent_config['action_space']
            agent = {'steering':SteeringActionAgent,
                     'velocity':VelocityActionAgent,
                     'trajectory':TrajectoryActionAgent}[action_space](i)
            self.bg_agents['controlled_cars'].append(agent)

    def is_in_collision(self,car):

        for obj in self.static_objects:
          if car.collides(obj):
              return True
        for key in self.dynamic_objects.keys():
            for i,obj in six.iteritems(self.dynamic_objects[key]):
                if car.collides(obj):
                    return True
        return False


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
        if self.last_coll == self.time:
            return self.dynamic_collisions, self.static_collisions, self.controlled_car_collisions
        self.dynamic_collisions, self.static_collisions, self.controlled_car_collisions = [], [], []
        self.last_coll = self.time

        #TODO Fix this. Controlled cars can't collide with background cars
        for key in self.dynamic_objects.keys():
            for i, dobj in self.dynamic_objects[key].items():
                i = int(i)

                for j, sobj in enumerate(self.static_objects):
                    if dobj.collides(sobj):
                        self.static_collisions.append([i, j, key, 'static'])

                for inner_key in self.dynamic_objects.keys():
                    for j, dobj1 in self.dynamic_objects[inner_key].items():
                        j = int(j)
                        if (not (i == j and key == inner_key)) and dobj.collides(dobj1):
                            self.dynamic_collisions.append([i, j,key, inner_key])
                            if key == 'controlled_cars':
                                self.controlled_car_collisions.append([i, j,key, inner_key])

        return self.dynamic_collisions, self.static_collisions, self.controlled_car_collisions


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

        dynamic_collisions, static_collisions, _ = self.get_collisions()
        for coll in dynamic_collisions:
            id1, id2, t1, t2 = coll
            if (agentnum, type_of_agent) in [(id1, t1), (id2, t2)]:
                return True
        for coll in static_collisions:
            id1, id2, t1, t2 = coll
            if (agentnum, type_of_agent) is (id1, t1):
                return True
        return False

    def collides_any_dynamic(self, agentnum,type_of_agent = 'background_cars'):
        dynamic_collisions, static_collisions, _ = self.get_collisions()

        for coll in dynamic_collisions:
            id1, id2, t1, t2 = coll
            if (agentnum, type_of_agent) in [(id1, t1), (id2, t2)]:
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

    def get_observations(self, observation_type):
        """
        Returns a set

        Parameters
        ----------
        agentnum : int
            The index of the object to query

        Returns
        -------
        float
            Distance to nearest collideable object
        """
