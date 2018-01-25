from gym_urbandriving.state.state import PositionState
from gym_urbandriving.assets import Terrain, Lane, Street, Sidewalk,\
    Pedestrian, Car, TrafficLight
import numpy as np
import random

class SimpleRoundaboutState(PositionState):
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
    static_objects = [Terrain(500, 500, radius=100),
                      Lane(140, 450, 280, 100, angle=-np.pi),
                      Lane(140, 550, 280, 100),
                      Lane(860, 450, 280, 100, angle=-np.pi),
                      Lane(860, 550, 280, 100),
                      Lane(450, 140, 280, 100, angle=-(np.pi/2)),
                      Lane(550, 140, 280, 100, angle=(np.pi/2)),
                      Lane(450, 860, 280, 100, angle=-(np.pi/2)),
                      Lane(550, 860, 280, 100, angle=(np.pi/2)),
                      Lane(500, 500, angle=0, curvature=(np.pi/2), inner_r=100, outer_r=250),
                      Lane(500, 500, angle=(np.pi/2), curvature=(np.pi/2), inner_r=100, outer_r=250),
                      Lane(500, 500, angle=np.pi, curvature=(np.pi/2), inner_r=100, outer_r=250),
                      Lane(500, 500, angle=270, curvature=(np.pi/2), inner_r=100, outer_r=250),
                      ]
    static_objects += [Terrain(200, 200, 400, 400, excludes=static_objects),
                       Terrain(800, 200, 400, 400, excludes=static_objects),
                       Terrain(200, 800, 400, 400, excludes=static_objects),
                       Terrain(800, 800, 400, 400, excludes=static_objects),
    ]


    def randomize(self):
        """
        Randomly generates car and pedestrian positions
        """
        self.dynamic_objects = []
        while len(self.dynamic_objects) < self.ncars:
            i = np.random.random_integers(0, 3) if len(self.dynamic_objects) else np.random.random_integers(0, 2)
            lane = random.choice([l for l in self.static_objects if type(l) == Lane])
            car = lane.generate_car()
            car.vel = 0
            if not any([car.collides(obj) for obj in self.static_objects+self.dynamic_objects]):
                self.dynamic_objects.append(car)
