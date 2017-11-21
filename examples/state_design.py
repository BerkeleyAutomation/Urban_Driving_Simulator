import gym_urbandriving as uds
from gym_urbandriving.state import PositionState
from gym_urbandriving.assets import Car, Terrain, Street, Lane, Sidewalk
import random

class CustomState(PositionState):
    static_objects = [Lane(175, 550, 350, 100, angle=-180),
                      Lane(175, 650, 350, 100, angle=-180),
                      Lane(175, 750, 350, 100),
                      Lane(175, 850, 350, 100),
                      Lane(825, 550, 350, 100, angle=-180),
                      Lane(825, 650, 350, 100, angle=-180),
                      Lane(825, 750, 350, 100),
                      Lane(825, 850, 350, 100),
                      Street(500, 700, 300, 400),
                      Lane(450, 250, 500, 100, angle=-90),
                      Lane(550, 250, 500, 100, angle=90),
                      Sidewalk(200, 475, 400, 50),
                      Sidewalk(800, 475, 400, 50),
                      Terrain(200, 225, 400, 450),
                      Terrain(800, 225, 400, 450),
                      Terrain(500, 950, 1000, 100)]

    def randomize(self):
        self.dynamic_objects = []
        lane_objs = [obj for obj in self.static_objects if type(obj) == Lane]
        sidewalk_objs = [obj for obj in self.static_objects if type(obj) == Sidewalk]

        for i in range(3):
            car = random.choice(lane_objs).generate_car()
            if not any([car.collides(obj) for obj in self.static_objects + self.dynamic_objects]):
                self.dynamic_objects.append(car)
        for i in range(2):
            man = random.choice(sidewalk_objs).generate_man()
            if not any([man.collides(obj) for obj in self.static_objects + self.dynamic_objects]):
                self.dynamic_objects.append(man)



vis = uds.PyGameVisualizer((800, 800))
init_state = CustomState()
env = uds.UrbanDrivingEnv(init_state=init_state,
                          visualizer=vis,
                          randomize=True)

env._render()

while(True):
    env._render()
