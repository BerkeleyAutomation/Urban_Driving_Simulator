import numpy as np
from gym_urbandriving.assets.primitives.rectangle import Rectangle
from gym_urbandriving.assets.primitives.circle import Circle
from gym_urbandriving.assets.primitives.shape import Shape
from gym_urbandriving.assets.terrain import Terrain
from gym_urbandriving.assets.sidewalk import Sidewalk
from gym_urbandriving.assets.pedestrian import Pedestrian

from gym import spaces

class Car(Rectangle):
    """
    Represents a point-model car.

    Parameters
    ----------
    x : float
        Starting x coordinate of car's center
    y : float
        Starting y coordinate of car's center
    angle : float
        Starting angle of car in world space
    vel : float
        Starting velocity of car

    Attributes
    ----------
    vel : float
        Forwards velocity of car
    max_vel : float
        Maximum allowable velocity of this car
    xdim : float
        Length of car
    ydim : float
        Width of car

    """
    def __init__(self, x, y, xdim=60, ydim=30, angle=0.0, vel=0.0,
                 max_vel=7.5, mass=100.0):
        Rectangle.__init__(self, x, y, xdim, ydim, angle, mass=mass, sprite="grey_car.png")
        self.vel = vel
        self.max_vel = max_vel


    def step(self, action, info_dict=None):
        """
        Updates the car for one timestep based on point model
        
        Parameters
        ----------
        action: 1x2 array,
            steering / acceleration action.
        info_dict: dict
            Unused, contains information about the environment.
        """
        self.shapely_obj = None
        if action is None:
            action_steer, action_acc = 0.0, 0.0
        else:
            action_steer, action_acc = action
        self.angle += action_steer
        self.angle %= 360.0
        self.angle = self.angle
        acc = action_acc
        acc = max(min(self.acc, self.max_vel - self.vel), -self.max_vel)

        t = 1
        dist = self.vel * t + 0.5 * acc * (t ** 2)
        dx = dist * np.cos(np.radians(self.angle))
        dy = dist * -np.sin(np.radians(self.angle))
        self.x += dx
        self.y += dy
        self.vel += acc
        self.vel = max(min(self.vel, self.max_vel), -self.max_vel)

    def get_state(self):
        """
        Get state.
        Returns---
            state: 1x3 array, contains x, y, angle of car.
            info_dict: dict, contains information about car.
        """
        return self.x, self.y, self.x_dim, self.y_dim, self.angle

    def can_collide(self, other):
        """
        Specifies whether this object can collide with another object
        """
        from gym_urbandriving.assets.kinematic_car import KinematicCar
        from gym_urbandriving.assets.lane import Lane
        if type(other) in {Terrain, Sidewalk, Car, KinematicCar, Pedestrian}:
            return True

        if type(other) is Lane:
            a = abs(self.angle - other.angle) % 360
            return a > 90 and a < 270
        return False
