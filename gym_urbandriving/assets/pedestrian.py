import numpy as np
from gym_urbandriving.assets.primitives.circle import Circle
from gym_urbandriving.assets.terrain import Terrain

class Pedestrian(Circle):
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
    def __init__(self, x, y, radius=17, angle=0.0, vel=0.0, acc=0.0, max_vel=2.0, mass=100.0):
        Circle.__init__(self, x, y, radius, angle, sprite="person.png")
        self.vel = vel
        self.acc = acc
        self.max_vel = max_vel
        self.mass = mass
        self.angle = angle


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
        if action is None:
            action_steer, action_acc = 0.0, 0.0
        else:
            action_steer, action_acc = action
        self.angle += action_steer
        self.angle &= 2*np.pi
        self.acc = action_acc
        self.acc = max(min(self.acc, self.max_vel - self.vel), -self.vel)

        t = 1
        dist = self.vel * t + 0.5 * self.acc * (t ** 2)
        dx = dist * np.cos(self.angle)
        dy = dist * -np.sin(self.angle)
        self.x += dx
        self.y += dy
        self.vel += self.acc
        self.vel = max(min(self.vel, self.max_vel), 0.0)
        
    def get_state(self):
        """
        Get state. 
        Returns:
            state: 1x3 array, contains x, y, angle of car.
            info_dict: dict, contains information about car.
        """
        return self.x,self.y,self.x_dim,self.y_dim,self.angle


    def can_collide(self, other):
        from gym_urbandriving.assets import Car
        if type(other) in {Terrain, Car}:
            return True
        return False
