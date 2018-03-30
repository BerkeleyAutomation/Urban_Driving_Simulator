from gym_urbandriving.state.state import PositionState
from gym_urbandriving.assets import Terrain, Lane, Street, Sidewalk,\
    Pedestrian, Car, TrafficLight
import numpy as np
from gym_urbandriving.agents import *
from gym_urbandriving.assets import Car, TrafficLight, CrosswalkLight
import random
from copy import deepcopy

class SimpleIntersectionState(PositionState):
    """
    Instance of a :class:`PositionState` describing a four-way intersection
    
    Parameters
    ----------
    ncars : int
        Number of cars to generate
    nped : int
        Number of pedestrians to generate
    traffic_lights : bool
        Whether or not to generate traffic lights
    """
    static_objects = [Terrain(175, 175, 350, 350),
                      Terrain(825, 175, 350, 350),
                      Terrain(175, 825, 350, 350),
                      Terrain(825, 825, 350, 350),
                      Lane(200, 450, 400, 100, angle=-np.pi),
                      Lane(200, 550, 400, 100),
                      Lane(800, 450, 400, 100, angle=-np.pi),
                      Lane(800, 550, 400, 100),
                      Lane(450, 200, 400, 100, angle=-(np.pi/2)),
                      Lane(550, 200, 400, 100, angle=(np.pi/2)),
                      Lane(450, 800, 400, 100, angle=-(np.pi/2)),
                      Lane(550, 800, 400, 100, angle=(np.pi/2)),
                      Street(500, 500, 200, 200),
                      Sidewalk(200, 375, 400, 50),
                      Sidewalk(200, 625, 400, 50),
                      Sidewalk(800, 375, 400, 50, angle=-np.pi),
                      Sidewalk(800, 625, 400, 50, angle=-np.pi),
                      Sidewalk(375, 175, 350, 50, angle=-(np.pi/2)),
                      Sidewalk(625, 175, 350, 50, angle=-(np.pi/2)),
                      Sidewalk(375, 825, 350, 50, angle=(np.pi/2)),
                      Sidewalk(625, 825, 350, 50, angle=(np.pi/2))
    ]

    def randomize(self):
        """
        Randomly generates car and pedestrian positions
        """
        car_goals = "NSEW"
        self.dynamic_objects = {}

        self.dynamic_objects['controlled_cars'] = {}
        self.dynamic_objects['background_cars'] = {}
        self.dynamic_objects['pedestrians'] = {}
        self.dynamic_objects['traffic_lights'] = {}

        self.dynamic_objects_lane_indices = []

        lanes = [Lane(450, 200, 400, 100, angle=-(np.pi/2)),
                    Lane(550, 800, 400, 100, angle=(np.pi/2)),
                    Lane(800, 450, 400, 100, angle=-np.pi),
                    Lane(200, 550, 400, 100)]

        car_index = 0

        for car_index in range(self.agent_config['controlled_cars']):

            #Find a lane to generate car on 

            while True:
              start = np.random.random_integers(0, 3)
              lane = lanes[start]
              car = lane.generate_car(self.car_model)


              if not self.is_in_collision(car):
                  self.dynamic_objects['controlled_cars'][str(car_index)] = car
                  self.dynamic_objects['controlled_cars'][str(car_index)].destination = self.assign_goal_states(start)
                  break

        for car_index in range(self.agent_config['background_cars']):

            #Find a lane to generate car on 
            while True:
              start = np.random.random_integers(0, 3)
              lane = lanes[start]
              car = lane.generate_car(self.car_model)


              if not self.is_in_collision(car):
                  self.dynamic_objects['background_cars'][str(car_index)] = car
                  self.dynamic_objects['background_cars'][str(car_index)].destination = self.assign_goal_states(start)
                  break


        if self.agent_config["use_pedestrians"]:
          while len(self.dynamic_objects) < self.ncars+self.nped:
              sidewalk = self.static_objects[-8:][np.random.random_integers(0, 7)]
              man = sidewalk.generate_man()
              man.vel = 2
              if not any([man.collides(obj) for obj in self.static_objects+self.dynamic_objects]):
                  self.dynamic_objects.append(man)
                
        if self.agent_config["use_traffic_lights"]:
            self.dynamic_objects['traffic_lights']['0'] = TrafficLight(600, 440, 0)
            self.dynamic_objects['traffic_lights']['1'] = TrafficLight(400, 560, -np.pi)
            self.dynamic_objects['traffic_lights']['2'] = TrafficLight(560, 600, -(np.pi/2), init_color="red")
            self.dynamic_objects['traffic_lights']['3'] = TrafficLight(440, 400, (np.pi/2), init_color="red")

        self.create_agents()


    def assign_goal_states(self, start_lane):
        """
        Randomly assigns goal states to the cars
        No two agents can go to the same goal 
        No goal can be on the same starting spot
        """
        sorted_goal = []

        #Goals organized in NSEW order
        goal_states = []
        goal_states.append([550,100,2,np.pi/2])
        goal_states.append([450,900,2,-np.pi/2])
        goal_states.append([900,550,2,0])
        goal_states.append([100,450,2,np.pi])

        del goal_states[start_lane]
        return random.choice(goal_states)


    def create_agents(self):

        self.agent_mappings = {Car:PlanningPursuitAgent,
                    TrafficLight:TrafficLightAgent, 
                    CrosswalkLight:CrosswalkLightAgent}

        self.bg_agents = {}

        for key in self.dynamic_objects.keys():
            if not key == 'controlled_cars':
              self.bg_agents[key] = []
              for i, index in enumerate(self.dynamic_objects[key]):
                  obj = self.dynamic_objects[key][index]
                  if type(obj) in self.agent_mappings:
                      self.bg_agents[key].append(self.agent_mappings[type(obj)](i))

        ###Hierachy Control for cars
        self.bg_agents['controlled_cars'] = []
        for i in range(self.agent_config['controlled_cars']):

          if self.agent_config['action_space'] == 'steering':
            self.bg_agents['controlled_cars'].append(SteeringActionAgent(i))
          elif self.agent_config['action_space'] == 'velocity':
            self.bg_agents['controlled_cars'].append(VelocityActionAgent(i))
          elif self.agent_config['action_space'] == 'trajectory':
            self.bg_agents['controlled_cars'].append(TrajectoryActionAgent(i))
          else:
            raise Exception('No Valid Action Space Specified. Please Change Config File')

    def is_in_collision(self,car):

        for obj in self.static_objects:
          if car.collides(obj):
            return True

        for key in self.dynamic_objects.keys():
            for i,obj in enumerate(self.dynamic_objects[key]):
              if car.collides(obj):
                return True

        return False

