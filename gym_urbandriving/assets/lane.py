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
        """
        Initializes lane as a Rectangle object

        Parameters
        ----------
        x : float, x position of the lane
        y : float, y position of the lane
        xdim : float, width of the lane
        ydim : float, height of the lane
        angle: float, angle in degrees 
        """
        Rectangle.__init__(self, x, y, xdim, ydim, angle=angle, sprite="lane.png", static=True);

    def generate_car(self, car_type="kinematic"):
        """
        Creates a car on this lane ready to drive into the intersection
        
        Parameters
        ----------
        car_type : "kinematic" or "point"
            Specifies dynamics model for the car
        Returns
        -------
        Car
            Generated Car object
        """
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
