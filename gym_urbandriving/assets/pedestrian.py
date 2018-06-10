import numpy as np
from gym_urbandriving.assets.primitives.circle import Circle
from gym_urbandriving.assets.primitives.dynamic_shape import DynamicShape
from gym_urbandriving.assets.terrain import Terrain
from gym_urbandriving.assets.crosswalk_light import CrosswalkLight

class Pedestrian(Circle, DynamicShape):
    """
    Represents a pedestrian as a circle
    
    Parameters
    ----------
    x : float
        Center x coordinate
    y : float
        Center y coordinate
    radius : float
        Size of the pedestrian
    angle : float
        Initial orientation, in degrees
    vel : float
        Initial velocity
    max_vel : float
        Maximum velocity
    mass : float
        Mass of pedestrian
    """
    def __init__(self, x, y, radius=12, angle=0.0, vel=0.0, acc=0.0, max_vel=2.0, mass=100.0, dynamics_model="point"):
        Circle.__init__(self, x, y, radius, angle, sprite="person.png")
        DynamicShape.__init__(self, 0, 0, max_vel, dynamics_model)
        self.vel = vel
        self.acc = acc
        self.mass = mass
        self.angle = angle
        self.last_action = None


    def step(self, action, info_dict=None):
        """
        Updates the pedestrian for one timestep.

        Parameters
        ----------
        action : 1x2 array
           Steering / acceleration action.
        info_dict : dict
           Contains information about the environment.
        """
        self.shapely_obj = None
        self.last_action = action
        if self.dynamics_model == "kinematic":
            self.x, self.y, self.vel, self.angle = self.kinematic_model_step(action, self.x, self.y, self.vel, self.angle)
        elif self.dynamics_model == "reeds_shepp":
            self.x, self.y, self.vel, self.angle = self.reeds_shepp_model_step(action, self.x, self.y, self.vel, self.angle)
        else:
            self.x, self.y, self.vel, self.angle = self.point_model_step(action, self.x, self.y, self.vel, self.angle)

    def get_state(self):
        """
        Get state. 
        Returns:
            state: 1x3 array, contains x, y, angle of car.
            info_dict: dict, contains information about car.
        """
        return self.x,self.y,self.angle


    def can_collide(self, other):
        from gym_urbandriving.assets import Car
        if type(other) in {Terrain, Car}:
            return True
        if type(other) in {CrosswalkLight} and other.color == 'red':
            e_angle = other.angle-self.angle
            if e_angle > np.pi:
                e_angle -= (np.pi*2)
            elif e_angle < -np.pi:
                e_angle += (np.pi*2)
            if abs(e_angle) < .1:
                return True

        return False

    def get_future_locations(self, horizon=5):
        from gym_urbandriving.agents import PedestrianAgent
        
        copy_state = self.get_state()
        start_obj = self.get_shapely_obj()
        for i in range(horizon):
            self.step(self.last_action)
        r = start_obj.union(self.get_shapely_obj())
        self.shapely_obj = None
        self.x, self.y, self.angle = copy_state
        return r
