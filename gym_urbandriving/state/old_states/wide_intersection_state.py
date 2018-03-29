from gym_urbandriving.state.state import PositionState
from gym_urbandriving.assets import Terrain, Lane, Street, Sidewalk,\
    Pedestrian, Car, TrafficLight
import numpy as np

class WideIntersectionState(PositionState):
    static_objects = [Terrain(125, 125, 250, 250),
                      Terrain(875, 125, 250, 250),
                      Terrain(125, 875, 250, 250),
                      Terrain(875, 875, 250, 250),
                      Lane(150, 450, 300, 100, angle=-np.pi),
                      Lane(150, 550, 300, 100),
                      Lane(850, 450, 300, 100, angle=-np.pi),
                      Lane(850, 550, 300, 100),
                      Lane(450, 150, 300, 100, angle=-(np.pi/2)),
                      Lane(550, 150, 300, 100, angle=(np.pi/2)),
                      Lane(450, 850, 300, 100, angle=-(np.pi/2)),
                      Lane(550, 850, 300, 100, angle=(np.pi/2)),
                      Lane(150, 350, 300, 100, angle=-np.pi),
                      Lane(150, 650, 300, 100),
                      Lane(850, 350, 300, 100, angle=-np.pi),
                      Lane(850, 650, 300, 100),
                      Lane(350, 150, 300, 100, angle=-(np.pi/2)),
                      Lane(650, 150, 300, 100, angle=(np.pi/2)),
                      Lane(350, 850, 300, 100, angle=-(np.pi/2)),
                      Lane(650, 850, 300, 100, angle=(np.pi/2)),
                      Street(500, 500, 400, 400),
                      Sidewalk(150, 275, 300, 50),
                      Sidewalk(150, 725, 300, 50),
                      Sidewalk(850, 275, 300, 50),
                      Sidewalk(850, 725, 300, 50),
                      Sidewalk(275, 125, 50, 250),
                      Sidewalk(725, 125, 50, 250),
                      Sidewalk(275, 875, 50, 250),
                      Sidewalk(725, 875, 50, 250),
    ]

    def randomize(self):
        self.dynamic_objects = []
        while len(self.dynamic_objects) < self.ncars:
            lane = [Lane(150, 550, 300, 100),
                    Lane(850, 450, 300, 100, angle=-np.pi),
                    Lane(450, 150, 300, 100, angle=-(np.pi/2)),
                    Lane(550, 850, 300, 100, angle=(np.pi/2)),
                    Lane(150, 650, 300, 100),
                    Lane(850, 350, 300, 100, angle=-np.pi),
                    Lane(350, 150, 300, 100, angle=-(np.pi/2)),
                    Lane(650, 850, 300, 100, angle=(np.pi/2)),
            ][np.random.random_integers(0, 7)]
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

        if self.traffic_lights:
            self.dynamic_objects.append(TrafficLight(700, 450, 0))
            self.dynamic_objects.append(TrafficLight(700, 350, 0))
            self.dynamic_objects.append(TrafficLight(300, 550, -np.pi))
            self.dynamic_objects.append(TrafficLight(300, 650, -np.pi))

            self.dynamic_objects.append(TrafficLight(550, 700, -(np.pi/2), initial_color="red"))
            self.dynamic_objects.append(TrafficLight(650, 700, -(np.pi/2), initial_color="red"))
            self.dynamic_objects.append(TrafficLight(450, 300, (np.pi/2), initial_color="red"))
            self.dynamic_objects.append(TrafficLight(350, 300, (np.pi/2), initial_color="red"))
