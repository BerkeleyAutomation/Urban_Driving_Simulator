from gym_urbandriving.assets.street import Street
from gym_urbandriving.assets.primitives import Rectangle
from gym_urbandriving.assets.kinematic_car import KinematicCar
import numpy as np


class Lane(Street):
    def __init__(self, x, y, xdim, ydim, angle=0.0):
        Rectangle.__init__(self, x, y, xdim, ydim, angle=angle, sprite="lane.png", static=True);

    def generate_car(self, car_type=KinematicCar):
        car = car_type(0, 0, angle=self.angle+np.random.uniform(-10, 10))
        angle = np.radians(-self.angle)
        rotation_mat = np.array([[np.cos(angle), -np.sin(angle)],
                                 [np.sin(angle), np.cos(angle)]])
        x = np.random.uniform(0-self.xdim/2+car.xdim/2,
                              0+self.xdim/2-car.xdim/2)
        y = np.random.uniform(0-self.ydim/2+car.ydim/2,
                              0+self.ydim/2-car.ydim/2)
        x, y = np.dot([x, y], rotation_mat.T)
        x, y = x+self.x, y+self.y
        car.x, car.y = x, y
        car.vel = np.random.uniform(0, 5)
        return car
