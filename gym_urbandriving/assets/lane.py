from gym_urbandriving.assets.street import Street
from gym_urbandriving.assets.primitives import Rectangle
from gym_urbandriving.assets.car import Car
import numpy as np


class Lane(Street):
    """
    Represents a lane of road. Lanes have directionality, so cars should drive in the
    right direction.

    Parameters
    ----------
    x : float
       Upper left x coordinate of the lane block
    y : float
       Upper left y coordinate of the lane block
    xdim : float
       Width of the lane block
    ydim : float
       Height of the lane block
    angle ; float
       In degrees, the rotation of the lane block.
    """
    def __init__(self, x, y, xdim, ydim, angle=0.0):
        Rectangle.__init__(self, x, y, xdim, ydim, angle=angle, sprite="lane.png", static=True);

    def generate_car(self, car_type="kinematic", randomize=True):
        """
        Generates a car on the lane, facing the right direction.

        Parameters
        ----------
        car_type : "kinematic" or "point"
            Specifies dynamics model for the car
        randomize : bool
            Specifies if the car's position is randomized

        Returns
        -------
        Car
            Generated Car object
        """
        if randomize:
            car = Car(0, 0, angle=self.angle+np.random.uniform(-10, 10),
                      dynamics_model=car_type)
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
        else:
            car = Car(0, 0, angle =self.angle,
                      dynamics_model=car_type)
            angle = np.radians(-self.angle)
            rotation_mat = np.array([[np.cos(angle), -np.sin(angle)],
                                     [np.sin(angle), np.cos(angle)]])
            x = -self.xdim/2+car.xdim/2
            y = 0
            x, y = np.dot([x, y], rotation_mat.T)
            x, y = x+self.x, y+self.y
            car.x, car.y = x, y
            return car
