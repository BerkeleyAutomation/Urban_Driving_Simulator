import numpy as np
from scipy.integrate import odeint


class DynamicShape():

    def __init__(self, l_r, l_f, max_vel, dynamics_model):
        self.l_r = l_r
        self.l_f = l_f
        self.max_vel = max_vel
        self.dynamics_model = dynamics_model
   
    def point_model_step(self, action, x, y, v, a, info_dict=None):
        """
        Updates the car for one timestep based on point model

        Parameters
        ----------
        action: 1x2 array,
            steering / acceleration action.
        info_dict: dict
            Unused, contains information about the environment.
        """
        if action is None:
            action_steer, action_acc = 0.0, 0.0
        else:
            action_steer, action_acc = action

        acc = action_acc
        acc = max(min(acc, self.max_vel - v), -self.max_vel)
        t = 1
        dist = v * t + 0.5 * acc * (t ** 2)
        dx = dist * np.cos(a)
        dy = dist * -np.sin(a)

        a += action_steer
        a %= 2*np.pi

        x += dx
        y += dy
        v += acc
        v = max(min(v, self.max_vel), -self.max_vel)

        return x, y, v, a

    def kinematic_model_step(self, action, x, y, v, a):
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

        # Unpack actions, convert angles to radians
        if action is None:
            action_steer, action_acc = 0.0, 0.0
        else:
            action_steer, action_acc = action

        action_steer = max(min(1, action_steer), -1)
        action_steer, rad_angle = np.radians(30*action_steer), a

        # Clamp acceleration if above maximum velocity
        if action_acc > self.max_vel - v:
            action_acc = self.max_vel - v
        elif action_acc < -self.max_vel - v:
            action_acc = - self.max_vel - v

        # Differential equations
        ode_state = [x, y, v, rad_angle]
        aux_state = (action_acc, action_steer)
        t = np.arange(0.0, 1.1, 0.1)
        delta_ode_state = odeint(integrator, ode_state, t, args=aux_state)
        x, y, vel, angle = delta_ode_state[-1]

        # Update car
        x, y, v, a = x, y, vel, angle
        a %= 2*np.pi
        assert ( a <= 2*np.pi)
        return x, y, v, a


    def reeds_shepp_model_step(self, action, x, y, v, a):
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

        if action is None:
            action is [0, 0]
        u2, u1 = action
        u2 = u2 * 0.015
        if u1 > self.max_vel - v:
            u1 = self.max_vel - v
        elif u1 < -self.max_vel - v:
            u1 = - self.max_vel - v
        ode_state = [x, y, v, a]
        aux_state = (u1, u2)
        t = np.arange(0.0, 1.1, 0.1)
        delta_ode_state = odeint(integrator, ode_state, t, args=aux_state)
        x, y, vel, angle = delta_ode_state[-1]

        # Update car
        x, y, v, a = x, y, vel, angle
        a %= 2*np.pi

        return x, y, v, a
