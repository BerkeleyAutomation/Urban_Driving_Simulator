import numpy as np
import json
import pygame
from six import iteritems
import constraint as csp
from shapely import speedups
if speedups.available:
    speedups.enable()

from fluids.state import State
from fluids.assets import *
from fluids.utils import fluids_assert, dist_reward, print
from fluids.actions import *
from fluids.consts import *
from fluids.obs import GridObservation




class FluidSim(object):
    def __init__(self,
                 state               =STATE_CITY,
                 visualization_level =1,
                 controlled_cars     =1,
                 background_cars     =0,
                 background_peds     =0,
                 fps                 =30,
                 randomize           =True,
                 control_space       =CTRL_STEERING,
                 obs_space           =OBS_NONE,
                 background_control  =BACKGROUND_NULL,
                 reward_fn           =REWARD_NONE,
                 screen_dim          =800):

        if state in [STATE_CITY]:
            self.state = State(layout          =state,
                               controlled_cars =controlled_cars,
                               background_cars =background_cars,
                               background_peds =background_peds,
                               vis_level       =visualization_level)
        else:
            self.state = State
        self.screen_dim            = (int(screen_dim * self.state.dimensions[0] / self.state.dimensions[1]),
                                      screen_dim)
        if visualization_level:
            pygame.init()
            pygame.font.init()
            self.fps_font    = pygame.font.SysFont('Mono', 30)
            self.fps_surface = self.fps_font.render("0", False, (0, 0, 0))
            self.surface     = pygame.display.set_mode(self.screen_dim)
        self.clock   = pygame.time.Clock()

        self.randomize             = randomize
        self.control_interpreter   = {CTRL_STEERING  : lambda a: a}[control_space]
        self.obs_space             = obs_space
        self.reward_fn             = {REWARD_DIST    : dist_reward,
                                      REWARD_NONE    : lambda s : 0}[reward_fn]
        self.background_control    = background_control
        self.vis_level             = visualization_level

        self.fps                   = fps
        self.render()

    def render(self):
        if self.vis_level:
            self.clock.tick(self.fps)
            self.surface.blit(pygame.transform.scale(self.state.get_static_surface(),
                                                     self.screen_dim), (0, 0))

            self.surface.blit(pygame.transform.scale(self.state.get_dynamic_surface(),
                                                     self.screen_dim), (0, 0))

            if not self.state.time % 30:
                self.fps_surface = self.fps_font.render(str(int(self.clock.get_fps())), False, (0, 0, 0))
            self.surface.blit(self.fps_surface, (0, 0))
            pygame.display.flip()
        else:
            self.clock.tick(0)
            if not self.state.time % 60:
                print("FPS: " + str(int(self.clock.get_fps())))    

        
        
    def get_control_keys(self):
        return self.state.controlled_cars.keys()

    def step(self, actions):
        # Convert the hierarchical input into steering-acceleration
        for k, v in iteritems(actions):
            actions[k] = self.control_interpreter(v)

        # Get background vehicle and pedestrian controls
        actions.update(self.get_background_actions())

        # Simulate the objects
        for k, v in iteritems(self.state.dynamic_objects):
            self.state.objects[k].step(actions[k] if k in actions else None)

        self.state.time += 1


        # Get collisions and observations
        collisions = self.state.get_controlled_collisions()
        observations = {k:c.make_observation(self.obs_space)
                        for k, c in iteritems(self.state.controlled_cars)}
        reward = self.reward_fn(self.state)
        self.render()
        return collisions, observations, reward

    def get_background_actions(self):
        if self.background_control == BACKGROUND_NULL or len(self.state.background_cars) == 0:
            return {}

        futures = { k:o.get_future_shape() for k, o in iteritems(self.state.background_cars)}
        futures_lights = [(o, o.get_future_color()) for o in self.state.type_map[TrafficLight]]

        keys = [k for k in futures]
        problem = csp.Problem()

        for k in futures:
            problem.addVariable(k, [(0,self.state.objects[k].shapely_obj, k), (1, futures[k], k)])
        fast_map = {}
        for k1x in range(len(keys)):
            k1 = keys[k1x]
            car1 = self.state.objects[k1]
            for k2x in range(k1x + 1, len(keys)):
                k2 = keys[k2x]
                car2 = self.state.objects[k2]

                might_collide = futures[k1].intersects(futures[k2])
                if might_collide:
                    fast_map[(k1, k2, 0, 0)] = True
                    fast_map[(k1, k2, 0, 1)] = not futures[k2].intersects(car1.shapely_obj)
                    fast_map[(k1, k2, 1, 0)] = not futures[k1].intersects(car2.shapely_obj)
                    fast_map[(k1, k2, 1, 1)] = False
                    problem.addConstraint(lambda k1v, k2v :
                                          fast_map[k1v[2], k2v[2], k1v[0], k2v[0]],
                                          [k1, k2])
            for fl, flc in futures_lights:
                if flc == "red" and futures[k1].intersects(fl.shapely_obj) and not car1.intersects(fl):
                    problem.addConstraint(lambda k1v : not k1v[0], [k1])


        solution = problem.getSolution()
        return {k:VelocityAction(v[0]*3) for k, v in iteritems(solution)}

        fluids_assert(False, "Not implemented")
