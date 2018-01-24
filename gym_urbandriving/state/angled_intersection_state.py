from gym_urbandriving.state.state import PositionState
from gym_urbandriving.assets import Terrain, Lane, Street, Sidewalk,\
    Pedestrian, Car
import numpy as np

class AngledIntersectionState(PositionState):
    static_objects = [Terrain(500, 500, 1000, 1000),
                      # Terrain(825, 175, 350, 350),
                      # Terrain(175, 825, 350, 350),
                      # Terrain(825, 825, 350, 350),
                      Lane(200, 450, 400, 100, angle=-180),
                      Lane(200, 550, 400, 100),
                      Lane(800, 450, 400, 100, angle=-180),
                      Lane(800, 550, 400, 100),
                      Lane(340, 200, 600, 100, angle=-60),
                      Lane(450, 200, 600, 100, angle=120),
                      Lane(690, 800, 600, 100, angle=-60),
                      Lane(800, 800, 600, 100, angle=120),
        
                      Street(570, 500, 350, 200),
                      # Sidewalk(200, 375, 400, 50),
                      # Sidewalk(200, 625, 400, 50),
                      # Sidewalk(800, 375, 400, 50),
                      # Sidewalk(800, 625, 400, 50),
                      # Sidewalk(375, 175, 50, 350),
                      # Sidewalk(625, 175, 50, 350),
                      # Sidewalk(375, 825, 50, 350),
                      # Sidewalk(625, 825, 50, 350),
    ]

    def randomize(self):
        
        self.dynamic_objects = []
        while len(self.dynamic_objects) < self.ncars:
            lane = [Lane(200, 450, 400, 100, angle=-180),
                    Lane(200, 550, 400, 100),
                    Lane(800, 450, 400, 100, angle=-180),
                    Lane(800, 550, 400, 100),
                    Lane(340, 200, 600, 100, angle=-60),
                    Lane(450, 200, 600, 100, angle=120),
                    Lane(690, 800, 600, 100, angle=-60),
                    Lane(800, 800, 600, 100, angle=120),
            ][np.random.random_integers(0, 3)]
            car = lane.generate_car()
            car.vel = 0
            # if not any([car.collides(obj) for obj in self.static_objects+self.dynamic_objects]):
            self.dynamic_objects.append(car)
       
