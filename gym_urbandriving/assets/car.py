from gym_urbandriving.assets.primitives.rectangle import Rectangle
from gym_urbandriving.assets.primitives.circle import Circle
from gym_urbandriving.assets.primitives.shape import Shape
from gym_urbandriving.assets.primitives.dynamic_shape import DynamicShape
from gym_urbandriving.assets.terrain import Terrain
from gym_urbandriving.assets.sidewalk import Sidewalk
from gym_urbandriving.assets.pedestrian import Pedestrian
from gym_urbandriving.assets.traffic_light import TrafficLight

from gym import spaces
import numpy as np

class Car(Rectangle, DynamicShape):
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
    def __init__(self, x, y, xdim=80, ydim=40, angle=0.0, vel=0.0,
                 max_vel=5, mass=100.0, dynamics_model="kinematic", destination=None,
                 trajectory=None):
        Rectangle.__init__(self, x, y, xdim, ydim, angle, mass=mass, sprite="blue_car.png")
        l_f = l_r = self.ydim / 2.0
        DynamicShape.__init__(self, l_r, l_f, max_vel, dynamics_model)
        self.vel = vel
        self.max_vel = max_vel
        self.dynamics_model = dynamics_model
        self.destination = destination
        self.trajectory = trajectory
        self.l_f = self.l_r = self.ydim / 2.0

    def at_goal(self, state):
        """
        Returns if this car is at its goal destination, if specified.
        Goal destination must be either in 'NSEW' or a coordinate pair
        """
        if not self.destination:
            return False
        elif self.destination == 'N':
            return self.y < 0
        elif self.destination == 'S':
            return self.y > state.dimensions[1]
        elif self.destination == 'W':
            return self.x < 0
        elif self.destination == 'E':
            return self.x > state.dimensions[0]
        else:
            return self.contains_point(self.destination[:2])

    def step(self, action):
        """
        Updates this object given this action input

        Parameters
        ----------
        action :
            The action to take
        """
        self.shapely_obj = None

        if self.dynamics_model == "kinematic":
            self.x, self.y, self.vel, self.angle = self.kinematic_model_step(action, self.x, self.y, self.vel, self.angle)
        elif self.dynamics_model == "reeds_shepp":
            self.x, self.y, self.vel, self.angle = self.reeds_shepp_model_step(action, self.x, self.y, self.vel, self.angle)
        else:
            self.x, self.y, self.vel, self.angle = self.point_model_step(action, self.x, self.y, self.vel, self.angle)

    def set_pos(self, x, y, vel, angle):
        self.shapely_obj = None
        angle = (angle + 2*np.pi) % (2*np.pi)
        self.x, self.y, self.vel, self.angle = x, y, vel, angle

    def get_state(self):
        """
        Get state.
        Returns---
            state: 1x3 array, contains x, y, angle of car.
            info_dict: dict, contains information about car.
        """
        return self.x, self.y, self.angle, self.vel

    def can_collide(self, other):
        """
        Specifies whether this object can collide with another object

        Parameters
        ----------
        other :
            Object to test collision against

        Returns
        -------
        bool
           True if this object can collide with other
        """
        from gym_urbandriving.assets.lane import Lane
        if type(other) in {Terrain, Sidewalk, Car, Pedestrian}:
            return True

        if type(other) in {TrafficLight} and other.color == 'red':
            return True

        if type(other) is Lane:
            a = abs(self.angle % (2*np.pi) - other.angle % (2*np.pi)) % (2*np.pi)
            return a > np.pi / 2  and a < 3*np.pi / 2
        return False
