from gym_urbandriving.state.state import PositionState
from gym_urbandriving.assets import Terrain, Lane, Street, Sidewalk,\
    Pedestrian, Car, TrafficLight
import numpy as np
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
        self.dynamic_objects = []
        self.dynamic_objects_lane_indices = []
        while len(self.dynamic_objects) < self.ncars:
            start = np.random.random_integers(0, 3)
            lane = [Lane(450, 200, 400, 100, angle=-(np.pi/2)),
                    Lane(550, 800, 400, 100, angle=(np.pi/2)),
                    Lane(800, 450, 400, 100, angle=-np.pi),
                    Lane(200, 550, 400, 100)][start]
            car = lane.generate_car(self.car_model)
            if not any([car.collides(obj) for obj in self.static_objects+self.dynamic_objects]):
                self.dynamic_objects.append(car)
                self.dynamic_objects_lane_indices.append(start)
        self.assign_goal_states(self.dynamic_objects_lane_indices)

        while len(self.dynamic_objects) < self.ncars+self.nped:
            sidewalk = self.static_objects[-8:][np.random.random_integers(0, 7)]
            man = sidewalk.generate_man()
            man.vel = 2
            if not any([man.collides(obj) for obj in self.static_objects+self.dynamic_objects]):
                self.dynamic_objects.append(man)
                
        if self.traffic_lights:
            self.dynamic_objects.append(TrafficLight(600, 440, 0))
            self.dynamic_objects.append(TrafficLight(400, 560, -np.pi))
            self.dynamic_objects.append(TrafficLight(560, 600, -(np.pi/2), initial_color="red"))
            self.dynamic_objects.append(TrafficLight(440, 400, (np.pi/2), initial_color="red"))


    def assign_goal_states(self, lane_orders):
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


        for i in range(len(lane_orders)):
          gs = deepcopy(goal_states)
          del gs[lane_orders[i]]
          self.dynamic_objects[i].destination = random.choice(gs)

        """
        #Lanes that cannot be assigned 
        forbidden_lanes = []

        for lane in lane_orders:

            #append current lane to constraint set
            forbidden_lanes.append(lane)

            while True:
                random_lane = np.random.random_integers(0, 3)
                if random_lane not in forbidden_lanes:
                    #remove current lane from constraint set
                    forbidden_lanes.pop()
                    #add the assigned lane
                    forbidden_lanes.append(random_lane)
                    break;

            sorted_goal.append(goal_states[random_lane])

        for i in range(len(sorted_goal)):
          self.dynamic_objects[i].destination = sorted_goal[i]
        """
