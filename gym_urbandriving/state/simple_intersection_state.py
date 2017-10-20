from gym_urbandriving.state.state import PositionState
from gym_urbandriving.assets import Terrain, Lane, Street, Sidewalk,\
    KinematicCar, Pedestrian, Car
import numpy as np

class SimpleIntersectionState(PositionState):
    static_objects = [Terrain(175, 175, 350, 350),
                      Terrain(825, 175, 350, 350),
                      Terrain(175, 825, 350, 350),
                      Terrain(825, 825, 350, 350),
                      Lane(200, 450, 400, 100, angle=-180),
                      Lane(200, 550, 400, 100),
                      Lane(800, 450, 400, 100, angle=-180),
                      Lane(800, 550, 400, 100),
                      Lane(450, 200, 400, 100, angle=-90),
                      Lane(550, 200, 400, 100, angle=90),
                      Lane(450, 800, 400, 100, angle=-90),
                      Lane(550, 800, 400, 100, angle=90),
                      Street(500, 500, 200, 200),
                      Sidewalk(200, 375, 400, 50),
                      Sidewalk(200, 625, 400, 50),
                      Sidewalk(800, 375, 400, 50),
                      Sidewalk(800, 625, 400, 50),
                      Sidewalk(375, 175, 50, 350),
                      Sidewalk(625, 175, 50, 350),
                      Sidewalk(375, 825, 50, 350),
                      Sidewalk(625, 825, 50, 350),
    ]

    def __init__(self, ncars=4, nped=2):
        self.ncars = ncars
        self.nped = nped
        PositionState.__init__(self)
        self.randomize()

    def randomize(self):
        self.dynamic_objects = []
        while len(self.dynamic_objects) < self.ncars:
            lane = [Lane(200, 550, 400, 100),
                    Lane(800, 450, 400, 100, angle=-180),
                    Lane(450, 200, 400, 100, angle=-90),
                    Lane(550, 800, 400, 100, angle=90)
            ][np.random.randint(0,3)]
            car = lane.generate_car()
            car.vel = 0
            if not any([car.collides(obj) for obj in self.static_objects+self.dynamic_objects]):
                self.dynamic_objects.append(car)
        while len(self.dynamic_objects) < self.ncars+self.nped:
            sidewalk = [Sidewalk(200, 375, 400, 50),
                        Sidewalk(200, 625, 400, 50),
                        Sidewalk(800, 375, 400, 50),
                        Sidewalk(800, 625, 400, 50),
                        Sidewalk(375, 175, 50, 350),
                        Sidewalk(625, 175, 50, 350),
                        Sidewalk(375, 825, 50, 350),
                        Sidewalk(625, 825, 50, 350),
            ][np.random.random_integers(0, 1)]
            man = sidewalk.generate_man()
            man.vel = 2
            if not any([man.collides(obj) for obj in self.static_objects+self.dynamic_objects]):
                self.dynamic_objects.append(man)

