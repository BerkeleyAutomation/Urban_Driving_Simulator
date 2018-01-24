import numpy as np
from gym_urbandriving.assets.primitives.rectangle import Rectangle
from gym_urbandriving.assets.primitives.circle import Circle
from gym_urbandriving.assets.primitives.shape import Shape
from gym_urbandriving.assets.terrain import Terrain
from gym_urbandriving.assets.sidewalk import Sidewalk
from gym_urbandriving.assets.pedestrian import Pedestrian
from scipy.integrate import odeint

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
    def __init__(self, x, y, xdim=80, ydim=40, angle=0.0, vel=0.0,
                 max_vel=5, mass=100.0, dynamics_model="kinematic"):
        Rectangle.__init__(self, x, y, xdim, ydim, angle, mass=mass, sprite="grey_car.png")
        self.vel = vel
        self.max_vel = max_vel
        self.dynamics_model = dynamics_model
        self.l_f = self.l_r = self.ydim / 2.0

    def step(self, action):
        """
        Updates this object given this action input

        Parameters
        ----------
        action :
            The action to take
        """
        if self.dynamics_model == "kinematic":
            self.kinematic_model_step(action)
        elif self.dynamics_model == "reeds_shepp":
            self.reeds_shepp_model_step(action)
        else:
            self.point_model_step(action)

    def point_model_step(self, action, info_dict=None):
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
        acc = max(min(acc, self.max_vel - self.vel), -self.max_vel)
        t = 1
        dist = self.vel * t + 0.5 * acc * (t ** 2)
        dx = dist * np.cos(np.radians(self.angle))
        dy = dist * -np.sin(np.radians(self.angle))
        self.x += dx
        self.y += dy
        self.vel += acc
        self.vel = max(min(self.vel, self.max_vel), -self.max_vel)

    def kinematic_model_step(self, action):
        """
        Updates the car for one timestep.

        Args:
            action: 1x2 array, steering / acceleration action.
            info_dict: dict, contains information about the environment.
        """

        def integrator(state, t, acc, delta_f):
            """
            Calculates numerical values of differential
            equation variables for dynamics.
            SciPy ODE integrator calls this function.

            :
            state: 1x6 array, contains x, y, dx_body, dy_body, rad_angle, rad_dangle
                of car.
            t: float, timestep.
            mu: float, friction coefficient.
            delta_f: float, steering angle.
            a_f: float, acceleration.

            Returns:
            output: list, contains dx, dy, ddx_body, ddy_body, dangle, ddangle.
            """
            x, y, vel, rad_angle = state

            # Differential equations
            beta = np.arctan((self.l_r / (self.l_f + self.l_r)) * np.tan(delta_f))
            dx = vel * np.cos(rad_angle + beta)
            dy = vel * -np.sin(rad_angle + beta)
            dangle = (vel / self.l_r) * np.sin(beta)
            dvel = acc
            output = [dx, dy, dvel, dangle]
            return output

        self.shapely_obj = None
        if action is None:
            action = [0, 0]
        # Unpack actions, convert angles to radians
        delta_f, a = action
        delta_f, rad_angle = np.radians(10*delta_f), np.radians(self.angle)

        # Clamp acceleration if above maximum velocity
        if a > self.max_vel - self.vel:
            a = self.max_vel - self.vel
        elif a < -self.max_vel - self.vel:
            a = - self.max_vel - self.vel
        # Differential equations
        ode_state = [self.x, self.y, self.vel, rad_angle]
        aux_state = (a, delta_f)
        t = np.arange(0.0, 1.0, 0.1)
        delta_ode_state = odeint(integrator, ode_state, t, args=aux_state)
        x, y, vel, angle = delta_ode_state[-1]

        # Update car
        self.x, self.y, self.vel, self.angle = x, y, vel, np.rad2deg(angle)
        self.angle %= 360.0

    def reeds_shepp_model_step(self, action):
        """
        Updates the car for one timestep.

        Args:
            action: 1x2 array, steering / acceleration action.
            info_dict: dict, contains information about the environment.
        """
        def integrator(state, t, u1, u2):
            x, y, vel, rad_angle = state
            # Differential equations
            dx = vel * np.cos(rad_angle)
            dy = vel * -np.sin(rad_angle)
            dangle = vel * u2
            dvel = u1
            output = [dx, dy, dvel, dangle]
            return output
        self.shapely_obj = None
        if action is None:
            action is [0, 0]
        u2, u1 = action
        u2 = u2 * 0.015
        if u1 > self.max_vel - self.vel:
            u1 = self.max_vel - self.vel
        elif u1 < -self.max_vel - self.vel:
            u1 = - self.max_vel - self.vel
        ode_state = [self.x, self.y, self.vel, np.radians(self.angle)]
        aux_state = (u1, u2)
        t = np.arange(0.0, 1.0, 0.1)
        delta_ode_state = odeint(integrator, ode_state, t, args=aux_state)
        x, y, vel, angle = delta_ode_state[-1]

        # Update car
        self.x, self.y, self.vel, self.angle = x, y, vel, np.rad2deg(angle)
        self.angle %= 360.0


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

        if type(other) is Lane:
            a = abs(self.angle % 360 - other.angle % 360) % 360
            return a > 90 and a < 270
        return False
