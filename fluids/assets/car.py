import numpy as np
from scipy.integrate import odeint
import pygame
import random
import shapely
import shapely.ops

from fluids.assets.shape import Shape
from fluids.actions import *
from fluids.utils import PIDController, fluids_assert
from fluids.obs import *
from fluids.consts import *


def integrator(state, t, steer, acc, lr, lf):
    x, y, vel, angle = state

    beta = np.arctan((lr / (lf + lr) * np.tan(steer)))
    dx = vel * np.cos(angle + beta)
    dy = vel * -np.sin(angle + beta)
    dangle = vel / lr * np.sin(beta)
    dvel = acc
    return dx, dy, dvel, dangle

class Car(Shape):
    def __init__(self, vel=0, mass=400, max_vel=5,
                 planning_depth=20, **kwargs):
        from fluids.assets import Lane, Car, Pedestrian, TrafficLight, Terrain, Sidewalk, PedCrossing
        collideables = [Lane,
                        Car,
                        Pedestrian,
                        TrafficLight,
                        Terrain,
                        Sidewalk,
                        PedCrossing]
        Shape.__init__(self,
                       collideables=collideables,
                       color=(0x1d,0xb1,0xb0),#769BB0
                       xdim=70,
                       ydim=35,
                       **kwargs)

        self.l_r            = self.l_f = self.ydim / 2
        self.mass           = mass
        self.max_vel        = max_vel
        self.vel            = vel
        self.waypoints      = []
        self.trajectory     = []
        self.planning_depth = planning_depth
        self.PID_acc        = PIDController(1.0, 0, 0)
        self.PID_steer      = PIDController(2.0, 0, 0)
        self.last_action    = SteeringAccAction(0, 0)
        self.last_obs       = None
        self.last_distance  = 0
        self.last_to_goal   = 0
        self.stopped_time   = 0
        self.running_time   = 0

        self.last_blob_time = -1
        self.cached_blob    = self.get_future_shape()


    def make_observation(self, obs_space=OBS_NONE, **kwargs):
        if obs_space == OBS_NONE:
            self.last_obs = None
        elif obs_space == OBS_GRID:
            self.last_obs = GridObservation(self, **kwargs)
        elif obs_space == OBS_BIRDSEYE:
            self.last_obs = BirdsEyeObservation(self, **kwargs)
        elif obs_space:
            fluids_assert(False, "Observation space not legal")
        return self.last_obs

    def raw_step(self, steer, f_acc):
        steer = max(min(1, steer), -1)
        f_acc = max(min(1, f_acc), -1)
        steer = np.radians(30 * steer)
        acc = 100 * f_acc / self.mass

        if acc > self.max_vel - self.vel:
            acc = self.max_vel - self.vel
        elif acc < -self.max_vel - self.vel:
            acc = - self.max_vel - self.vel

        ode_state = [self.x, self.y, self.vel, self.angle]
        aux_state = (steer, acc, self.l_r, self.l_f)

        t = np.arange(0.0, 1.5, 0.5)
        delta_ode_state = odeint(integrator, ode_state, t, args=aux_state)
        x, y, vel, angle = delta_ode_state[-1]


        self.vel = vel
        self.update_points(x, y, angle)
        self.running_time += 1




    def step(self, action):

        distance_to_next = self.dist_to(self.waypoints[0])
        startx, starty = self.x, self.y

        if action == None:
            self.raw_step(0, 0)
            self.last_action = action
        elif type(action) == SteeringAccAction:
            self.raw_step(*action.get_action())
            self.last_action = action
        elif type(action) == SteeringAction:
            fluids_assert(False, "Cars cannot receive a raw steering action")
        elif type(action) == VelocityAction:
            steer, acc = self.PIDController(action).get_action()
            #steer += np.random.randn() * 0.5 * steer
            #acc += np.random.randn() * 0.5 * acc / 5
            self.raw_step(steer, acc)
            self.last_action = action
        elif type(action) == SteeringVelAction:
            steer, vel = action.get_action()
            _, acc = self.PIDController(VelocityAction(vel)).get_action()
            self.raw_step(steer, acc)
            self.last_action = action
        elif type(action) == LastValidAction:
            self.step(self.last_action)
            return
        else:
            fluids_assert(False, "Car received an illegal action")
        while len(self.waypoints) < self.planning_depth and len(self.waypoints) and len(self.waypoints[-1].nxt):
            next_edge = random.choice(self.waypoints[-1].nxt)
            next_waypoint = next_edge.out_p
            line = next_edge.shapely_obj
            # line = shapely.geometry.LineString([(self.waypoints[-1].x, self.waypoints[-1].y),
            #                                     (next_waypoint.x, next_waypoint.y)]).buffer(self.ydim*0.5)
            self.trajectory.append(((self.waypoints[-1].x, self.waypoints[-1].y),
                                    (next_waypoint.x, next_waypoint.y), line))
            self.waypoints.append(next_waypoint)

        self.last_to_goal = distance_to_next - self.dist_to(self.waypoints[0])
        self.last_distance = np.linalg.norm([self.x - startx, self.y - starty])
        if self.last_distance == 0:
            self.stopped_time += 1
        else:
            self.stopped_time = 0
        if len(self.waypoints) and self.intersects(self.waypoints[0]):
            self.waypoints.pop(0)
            if len(self.trajectory):
                self.trajectory.pop(0)

        return

    def PIDController(self, target_vel, update=True):

        target_vel = target_vel.get_action()

        if len(self.waypoints):
            target_x = self.waypoints[0].x
            target_y = self.waypoints[0].y
        else:
            target_x = self.x
            target_y = self.y

        ac2 = np.arctan2(self.y - target_y, target_x - self.x)
        self.angle = self.angle % (2 * np.pi)
        ang = self.angle if self.angle < np.pi else self.angle - 2 * np.pi

        e_angle = ac2 - ang

        if e_angle > np.pi:
            e_angle -= 2 * np.pi
        elif e_angle < -np.pi:
            e_angle += 2 * np.pi

        e_vel = target_vel - self.vel

        steer = self.PID_steer.get_control(e_angle, update=update)
        acc = self.PID_acc.get_control(e_vel, update=update)
        return SteeringAccAction(steer, acc)
    def can_collide(self, other):
        from fluids.assets import Lane, TrafficLight
        if type(other) is Lane:
            dangle = (self.angle - other.angle) % (2 * np.pi)
            if dangle > np.pi / 2 and dangle < 3 * np.pi / 2:
                return super(Car, self).can_collide(other)
            return False
        elif type(other) is TrafficLight:
            if other.color == (200, 0, 0):
                return super(Car, self).can_collide(other)
            return False
        return super(Car, self).can_collide(other)

    def get_future_shape(self):
        if self.last_blob_time != self.running_time:
            if len(self.waypoints) and len(self.trajectory):

                line = shapely.geometry.LineString([(self.waypoints[0].x, self.waypoints[0].y),
                                                    (self.x, self.y)]).buffer(20, resolution=2)
                buf = [t[2] for t in self.trajectory][:max(int(1+6*self.vel/self.max_vel), 0)]
                self.cached_blob = shapely.ops.cascaded_union([line] + buf)
            else:
                self.cached_blob = self.shapely_obj

        self.last_blob_time = self.running_time
        return self.cached_blob

    def render(self, surface, **kwargs):
        super(Car, self).render(surface, **kwargs)
        if "waypoints" not in self.__dict__:
            return
        if len(self.waypoints) and self.vis_level > 1:
            pygame.draw.line(surface,
                             (255, 0, 0),
                             (self.x, self.y),
                             (self.waypoints[0].x, self.waypoints[0].y),
                             2)
            for line in self.trajectory:
                pygame.draw.line(surface,
                                 (255, 0, 0),
                                 line[0],
                                 line[1],
                                 2)
        if len(self.waypoints) and self.vis_level > 4:
            blob = self.get_future_shape()

            traj_ob = list(zip(*(blob).exterior.coords.xy))

            pygame.draw.polygon(surface,
                                (175, 175, 175),
                                traj_ob,
                                5)
