import numpy as np
import json
import pygame
from six import iteritems
import constraint as csp
from copy import deepcopy

from shapely import speedups


if speedups.available:
    speedups.enable()

from fluids.state import State
from fluids.assets import *
from fluids.utils import *
from fluids.actions import *
from fluids.consts import *
from fluids.obs import GridObservation




class FluidSim(object):
    def __init__(self,
                 state               =STATE_CITY,
                 visualization_level =1,
                 render_on           =True,
                 controlled_cars     =1,
                 background_cars     =0,
                 background_peds     =0,
                 fps                 =30,
                 obs_space           =OBS_NONE,
                 obs_args            ={},
                 background_control  =BACKGROUND_NULL,
                 reward_fn           =REWARD_PATH,
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

        self.obs_space             = obs_space
        self.obs_args              = obs_args
        self.reward_fn             = {REWARD_PATH    : path_reward,
                                      REWARD_NONE    : lambda s : 0}[reward_fn]
        self.background_control    = background_control
        self.vis_level             = visualization_level
        self.render_on             = render_on
        self.fps                   = fps
        self.last_keys_pressed     = None
        self.render()

    def __del__(self):
        pygame.quit()

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
            pygame.event.pump()
            self.last_keys_pressed = pygame.key.get_pressed()
        else:
            self.clock.tick(0)
            if not self.state.time % 60:
                fluids_print("FPS: " + str(int(self.clock.get_fps())))    

        
    def get_control_keys(self):
        return self.state.controlled_cars.keys()

    def step(self, actions={}):
        for k, v in iteritems(actions):
            if type(v) == KeyboardAction:
                if self.last_keys_pressed:
                    keys = self.last_keys_pressed
                    acc = 1 if keys[pygame.K_UP] else -1 if keys[pygame.K_DOWN] else 0
                    steer = 1 if keys[pygame.K_LEFT] else -1 if keys[pygame.K_RIGHT] else 0
                    actions[k] = SteeringAction(steer, acc)
                else:
                    actions[k] = None    
            

        # Get background vehicle and pedestrian controls
        actions.update(self.get_background_actions())

        # Simulate the objects
        for k, v in iteritems(self.state.dynamic_objects):
            self.state.objects[k].step(actions[k] if k in actions else None)

        self.state.time += 1



        observations = {k:c.make_observation(self.obs_space, **self.obs_args)
                        for k, c in iteritems(self.state.controlled_cars)}
        reward_step = self.reward_fn(self.state)
        #print(reward_step)
        if self.render_on:
            self.render()
        return observations, reward_step

    def get_background_actions(self):
        if self.background_control == BACKGROUND_NULL or len(self.state.background_cars) == 0:
            return {}

        futures = { k:o.get_future_shape() for k, o in iteritems(self.state.type_map[Car])}
        futures_lights = [(o, o.get_future_color()) for k, o in iteritems(self.state.type_map[TrafficLight])]
        futures_crosswalks = [(o, o.get_future_color()) for k, o in iteritems(self.state.type_map[CrossWalkLight])]
        futures_peds = {k:o.get_future_shape() for k, o in iteritems(self.state.type_map[Pedestrian])}

        keys = list(futures.keys())
        ped_keys = list(futures_peds.keys())
        problem = csp.Problem()

        for k in futures:
            problem.addVariable(k, [(0, self.state.objects[k].shapely_obj, k), (1, futures[k], k)])
        for k in futures_peds:
            problem.addVariable(k, [(0, self.state.objects[k].shapely_obj, k), (1, futures_peds[k], k)])
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
            for k2x in range(len(ped_keys)):
                k2 = ped_keys[k2x]
                ped2 = self.state.objects[k2]
                might_collide = futures[k1].intersects(futures_peds[k2])
                if might_collide:
                    fast_map[(k1, k2, 0, 0)] = True
                    fast_map[(k1, k2, 0, 1)] = not futures_peds[k2].intersects(car1.shapely_obj)
                    fast_map[(k1, k2, 1, 0)] = not futures[k1].intersects(ped2.shapely_obj)
                    fast_map[(k1, k2, 1, 1)] = False
                    problem.addConstraint(lambda k1v, k2v:
                                          fast_map[k1v[2], k2v[2], k1v[0], k2v[0]],
                                          [k1, k2])
            for fl, flc in futures_lights:
                if flc == "red" and futures[k1].intersects(fl.shapely_obj) and not car1.intersects(fl):
                    problem.addConstraint(lambda k1v : not k1v[0], [k1])
        for k1x in range(len(ped_keys)):
            k1 = ped_keys[k1x]
            ped1 = self.state.objects[k1]
            for fl, flc in futures_crosswalks:
                if np.abs(ped1.angle - fl.angle) < np.pi / 2:
                    if flc == "red" and ped1.intersects(fl):
                        problem.addConstraint(lambda k1v: not k1v[0], [k1])


        solution = problem.getSolution()
        actions = {}
        for k, v in iteritems(solution):
            if k in self.state.background_cars:
                actions[k] = VelocityAction(v[0]*3)
            elif k in self.state.type_map[Pedestrian]:
                actions[k] = v[0]
                
        return actions

        fluids_assert(False, "Not implemented")
    def run_time(self):
        return self.state.time
