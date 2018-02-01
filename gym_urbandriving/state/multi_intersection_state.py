from gym_urbandriving.state.state import PositionState
from gym_urbandriving.assets import Terrain, Lane, Street, Sidewalk,\
    Pedestrian, Car, TrafficLight
import numpy as np

class MultiIntersectionState(PositionState):
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
        car_index_list = range(4)
        self.lane_order = []
        
        while len(self.dynamic_objects) < self.ncars:

            lanes = [Lane(450, 200, 400, 100, angle=-(np.pi/2)),
                    Lane(550, 800, 400, 100, angle=(np.pi/2)),
                    Lane(800, 450, 400, 100, angle=-np.pi),
                    Lane(200, 550, 400, 100)]


            ln_index = np.random.random_integers(0, len(car_index_list)-1)
           
            lane = lanes[car_index_list[ln_index]]

            car = lane.generate_car()

            car.vel = 0
            if not any([car.collides(obj) for obj in self.static_objects+self.dynamic_objects]):
                self.dynamic_objects.append(car)
                self.lane_order.append(car_index_list[ln_index])
                car_index_list.pop(ln_index)


            # car = lane.generate_car(self.car_model)
            # car.destination = goal
            # if not any([car.collides(obj) for obj in self.static_objects+self.dynamic_objects]):
            #     self.dynamic_objects.append(car)

        while len(self.dynamic_objects) < self.ncars+self.nped:
            sidewalk = [Sidewalk(200, 375, 400, 50),
                      Sidewalk(200, 625, 400, 50),
                      Sidewalk(800, 375, 400, 50, angle=-np.pi),
                      Sidewalk(800, 625, 400, 50, angle=-np.pi),
                      Sidewalk(375, 175, 350, 50, angle=-(np.pi/2)),
                      Sidewalk(625, 175, 350, 50, angle=-(np.pi/2)),
                      Sidewalk(375, 825, 350, 50, angle=(np.pi/2)),
                      Sidewalk(625, 825, 350, 50, angle=(np.pi/2))
            ][np.random.random_integers(0, 7)]
            man = sidewalk.generate_man()
            man.vel = 2
            if not any([man.collides(obj) for obj in self.static_objects+self.dynamic_objects]):
                self.dynamic_objects.append(man)
                
        if self.traffic_lights:
            self.dynamic_objects.append(TrafficLight(600, 440, 0))
            self.dynamic_objects.append(TrafficLight(400, 560, -np.pi))
            self.dynamic_objects.append(TrafficLight(560, 600, -(np.pi/2), initial_color="red"))
            self.dynamic_objects.append(TrafficLight(440, 400, (np.pi/2), initial_color="red"))



# class MultiIntersectionState(PositionState):
#     """
#     Instance of a :class:`PositionState` describing a four-way intersection
#     It has been augmented to sample states in a way for Imitation Learning Experiments
    
#     Parameters
#     ----------
#     ncars : int
#         Number of cars to generate
#     nped : int
#         Number of pedestrians to generate
#     traffic_lights : bool
#         Whether or not to generate traffic lights
#     """
#     static_objects = [Terrain(175, 175, 350, 350),
#                       Terrain(825, 175, 350, 350),
#                       Terrain(175, 825, 350, 350),
#                       Terrain(825, 825, 350, 350),
#                       Lane(200, 450, 400, 100, angle=np.rad2deg(-180)),
#                       Lane(200, 550, 400, 100),
#                       Lane(800, 450, 400, 100, angle=-np.rad2deg(-180)),
#                       Lane(800, 550, 400, 100),
#                       Lane(450, 200, 400, 100, angle=np.rad2deg(-90)),
#                       Lane(550, 200, 400, 100, angle=np.rad2deg(90)),
#                       Lane(450, 800, 400, 100, angle=np.rad2deg(-90)),
#                       Lane(550, 800, 400, 100, angle=np.rad2deg(90)),
#                       Street(500, 500, 200, 200),
#                       Sidewalk(200, 375, 400, 50),
#                       Sidewalk(200, 625, 400, 50),
#                       Sidewalk(800, 375, 400, 50, angle=np.rad2deg(-180)),
#                       Sidewalk(800, 625, 400, 50, angle=np.rad2deg(-180)),
#                       Sidewalk(375, 175, 350, 50, angle=np.rad2deg(-90)),
#                       Sidewalk(625, 175, 350, 50, angle=np.rad2deg(-90)),
#                       Sidewalk(375, 825, 350, 50, angle=np.rad2deg(90)),
#                       Sidewalk(625, 825, 350, 50, angle=np.rad2deg(90))
#     ]

#     def __init__(self, ncars=4, nped=2, traffic_lights=False):
#         self.ncars = ncars
#         self.nped = nped
#         self.traffic_lights = traffic_lights
#         PositionState.__init__(self)
        
#         self.randomize()
        

#     def randomize(self):
#         """
#         Randomly generates car and pedestrian positions
#         """
#         self.dynamic_objects = []
#         self.lane_order = []
#         car_index_list = range(4)

#         i = 0
#         while len(self.dynamic_objects) < self.ncars:
#             #randomely generate cars with replacement in lanes
#             lanes = [
#                 Lane(450, 200, 400, 100, angle=-90),
#                 Lane(550, 800, 400, 100, angle=90),
#                 Lane(800, 450, 400, 100, angle=-180),              
#                 Lane(200, 550, 400, 100),
#             ]
 

#             ln_index = np.random.random_integers(0, len(car_index_list)-1)
           
#             lane = lanes[car_index_list[ln_index]]


#             car = lane.generate_car()

#             car.vel = 0
#             if not any([car.collides(obj) for obj in self.static_objects+self.dynamic_objects]):
#                 self.dynamic_objects.append(car)
#                 self.lane_order.append(car_index_list[ln_index])
#                 car_index_list.pop(ln_index)
                

#         while len(self.dynamic_objects) < self.ncars+self.nped:
#             sidewalk = [Sidewalk(200, 375, 400, 50),
#                       Sidewalk(200, 625, 400, 50),
#                       Sidewalk(800, 375, 400, 50, angle=-180),
#                       Sidewalk(800, 625, 400, 50, angle=-180),
#                       Sidewalk(375, 175, 350, 50, angle=-90),
#                       Sidewalk(625, 175, 350, 50, angle=-90),
#                       Sidewalk(375, 825, 350, 50, angle=90),
#                       Sidewalk(625, 825, 350, 50, angle=90)
#             ][np.random.random_integers(0, 7)]
#             man = sidewalk.generate_man()
#             man.vel = 2
#             if not any([man.collides(obj) for obj in self.static_objects+self.dynamic_objects]):
#                 self.dynamic_objects.append(man)

#         if self.traffic_lights:
#             self.dynamic_objects.append(TrafficLight(600, 440, 0))
#             self.dynamic_objects.append(TrafficLight(400, 560, -180))
#             self.dynamic_objects.append(TrafficLight(560, 600, -90, initial_color="red"))
#             self.dynamic_objects.append(TrafficLight(440, 400, 90, initial_color="red"))

