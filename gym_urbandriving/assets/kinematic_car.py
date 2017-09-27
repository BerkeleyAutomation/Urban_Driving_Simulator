import numpy as np
import os
from scipy.integrate import odeint
from gym import spaces
from gym_urbandriving.assets.primitives.rectangle import Rectangle
from gym_urbandriving.assets.car import Car

class KinematicCar(Car):
    def __init__(self, x, y, xdim=100, ydim=50, angle=0.0, vel=0.0, acc=0.0, mass=100.0):
        Car.__init__(self, x, y, xdim, ydim, angle, vel, acc, mass=mass)
        self.l_f = self.l_r = self.ydim / 2.0

    def step(self, action):
        """
        Updates the car for one timestep.

        Args:
            action: 1x2 array, steering / acceleration action.
            info_dict: dict, contains information about the environment.
        """
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
        delta_ode_state = odeint(self.integrator, ode_state, t, args=aux_state)
        x, y, vel, angle = delta_ode_state[-1]

        # Update car
        self.x, self.y, self.vel, self.angle = x, y, vel, np.rad2deg(angle)
        self.angle %= 360.0

    def integrator(self, state, t, acc, delta_f):
        """
        Calculates numerical values of differential
        equation variables for dynamics.
        SciPy ODE integrator calls this function.

        Args:
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
