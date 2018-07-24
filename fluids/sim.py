import numpy as np
import json
import pygame
from six import iteritems
from ortools.constraint_solver import pywrapcp
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
    """
    This class controls the generation and simulation of the urban environment.

    Parameters
    ----------
    state: str
        Name of json layout file specifiying environment object positions. Default is "fluids_state_city"
    visualization_level: int
        0 is no visualization. Higher numbers turn on more debug visuals.
    controlled_cars: int
        Number of cars to accept external control for
    background_cars: int
        Number of cars to control with the background planner
    background_peds: int
        Number of pedestrians to control with the background planner
    fps: int
        If set to a positive number, caps the FPS of the simulator. If set to 0, FPS is unbound. Default is 30
    obs_space: str
        Controls what observation representation to return for controlled cars. fluids.BIRDSEYE or fluids.NONE
    screen_dim: int
        Height of the visualization screen. Default is 800
    """
    def __init__(self,
                 visualization_level =1,
                 fps                 =30,
                 obs_space           =OBS_NONE,
                 obs_args            ={},
                 background_control  =BACKGROUND_NULL,
                 reward_fn           =REWARD_PATH,
                 screen_dim          =800):

        self.state                 = None
        self.screen_dim            = screen_dim
        if visualization_level:
            pygame.init()
            pygame.font.init()
            self.fps_font    = pygame.font.SysFont('Mono', 30)
            self.fps_surface = self.fps_font.render("0", False, (0, 0, 0))
            #self.surface     = pygame.display.set_mode(self.screen_dim)
        self.clock   = pygame.time.Clock()

        self.obs_space             = obs_space
        self.obs_args              = obs_args
        self.reward_fn             = {REWARD_PATH    : path_reward,
                                      REWARD_NONE    : lambda s : 0}[reward_fn]
        self.background_control    = background_control
        self.vis_level             = visualization_level
        self.fps                   = fps
        self.last_keys_pressed     = None
        self.last_obs              = {}
        self.next_actions          = {}


    def __del__(self):
        pygame.quit()

    def set_state(self, state):
        """
        Sets the state to simulate
        
        Parameters
        ----------
        state: fluids.State
            State object to simulate
        """
        self.state = state
        self.multiagent_plan()
        state.update_vis_level(self.vis_level)

    def render(self):
        if not self.state:
            fluids_print("WARNING. Render called without calling set_state first")
            return
        if self.vis_level:
            self.clock.tick(self.fps)
            screen_dim = (int(self.screen_dim * self.state.dimensions[0] / self.state.dimensions[1]),
                          self.screen_dim)
            full_surface = pygame.Surface(self.state.dimensions)
            self.surface = pygame.display.set_mode(screen_dim)
            full_surface.blit(self.state.get_static_surface(), (0, 0))
            if self.vis_level > 2:
                full_surface.blit(self.state.get_static_debug_surface(), (0, 0))

            dynamic_surface = self.state.get_dynamic_surface()
            if self.vis_level > 2:
                for k, obs in iteritems(self.last_obs):
                    if obs:
                        obs.render(dynamic_surface)
            full_surface.blit(dynamic_surface, (0, 0))
            self.surface.blit(pygame.transform.scale(full_surface, screen_dim), (0, 0))
            if not self.state.time % 30:
                self.fps_surface = self.fps_font.render(str(int(self.clock.get_fps())), False, (0, 0, 0))
            self.surface.blit(self.fps_surface, (0, 0))
            pygame.display.flip()
            pygame.event.pump()
            self.last_keys_pressed = pygame.key.get_pressed()
            if self.last_keys_pressed[pygame.K_PERIOD]:
                self.vis_level += 1
                self.state.update_vis_level(self.vis_level)
                fluids_print("New visualization level: " + str(self.vis_level))
            elif self.last_keys_pressed[pygame.K_COMMA] and self.vis_level > 1:
                self.vis_level -= 1
                self.state.update_vis_level(self.vis_level)
                fluids_print("New visualization level: " + str(self.vis_level))
            if self.last_keys_pressed[pygame.K_o]:
                if self.obs_space == OBS_NONE:
                    self.obs_space = OBS_BIRDSEYE
                    fluids_print("Switching to observation: birdseye")
                elif self.obs_space == OBS_BIRDSEYE:
                    self.obs_space = OBS_GRID
                    fluids_print("Switching to observation: grid")
                else:
                    self.obs_space = OBS_NONE
                    fluids_print("Switching to observation: none")
        else:
            self.clock.tick(0)
            if not self.state.time % 60:
                fluids_print("FPS: " + str(int(self.clock.get_fps())))


    def get_control_keys(self):
        """
        Returns
        -------
        list of keys
            Keys for every controlled car in the scene
        """
        fluids_assert(self.state, "get_control_keys called without setting the state")
        return self.state.controlled_cars.keys()

    def step(self, actions={}):
        """
        Simulates one frame

        Parameters
        ----------
        actions : dict of (key -> action)
            Keys in dict should correspond to controlled cars.
            Action can be of type KeyboardAction, SteeringAction, SteeringAccAction, or VelocityAction


        Returns
        -------

        """
        fluids_assert(self.state, "step called without setting the state")

        car_keys = self.state.controlled_cars.keys()
        for k in list(self.next_actions):
            if k in car_keys:
                if type(actions[k]) == SteeringAction:
                    actions[k] = SteeringAccAction(actions[k].steer, self.state.dynamic_objects[k].PIDController(self.next_actions[k], update=False).acc)
                self.next_actions.pop(k)
        self.next_actions.update(actions)
        for k, v in iteritems(self.next_actions):
            if type(v) == KeyboardAction:
                if self.last_keys_pressed:
                    keys = self.last_keys_pressed
                    acc = 1 if keys[pygame.K_UP] else -1 if keys[pygame.K_DOWN] else 0
                    steer = 1 if keys[pygame.K_LEFT] else -1 if keys[pygame.K_RIGHT] else 0
                    self.next_actions[k] = SteeringAccAction(steer, acc)
                else:
                    self.next_actions[k] = None
            elif type(v) == SteeringAction:
                action = self.next_actions


        # Simulate the objects
        for k, v in iteritems(self.state.dynamic_objects):
            self.state.objects[k].step(self.next_actions[k] if k in self.next_actions else None)

        self.state.time += 1

        reward_step = self.reward_fn(self.state)
        #print(reward_step)

        # Get background vehicle and pedestrian controls
        self.multiagent_plan()

        return reward_step
    def get_observations(self, keys={}):
        """
        Get observations from controlled cars in the scene.

        Parameters
        ----------
        keys: dict of keys
            Keys should refer to cars in the scene
        Returns
        -------
        dict of (key -> FluidsObs)
            Dictionary mapping keys of controlled cars to FluidsObs object
        """
        fluids_assert(self.state, "get_observations called without setting the state")
        observations = {k:self.state.objects[k].make_observation(self.obs_space, **self.obs_args)
                        for k in keys}
        self.last_obs = observations
        return observations

    def get_supervisor_actions(self, action_type=SteeringAccAction, keys={}):
        """
        Get the actions assigned to the selected car by the FLUIDS multiagent planer

        Parameters
        ----------
        action_type: fluids.Action
            Type of action to return. VelocityAction, SteeringAccAction, and SteeringAction are currently supported
        keys: set
            Set of keys for controlled cars or background cars to return actions for
        Returns
        -------
        dict of (key -> fluids.Action)
            Dictionary mapping car keys to actions
        """
        if action_type == VelocityAction:
            return {k:self.next_actions[k] for k in keys}
        elif action_type == SteeringAccAction:
            return {k:self.state.dynamic_objects[k].PIDController(self.next_actions[k], update=False)
                    for k in keys}
        elif action_type == SteeringAction:
            return {k:self.state.dynamic_objects[k].PIDController(self.next_actions[k], update=False).asSteeringAction()
                    for k in keys}
        else:
            fluids_assert(false, "Illegal action type")

    def multiagent_plan(self):
        if self.background_control == BACKGROUND_NULL or len(self.state.background_cars) == 0:
            return {}

        futures = { k:o.get_future_shape() for k, o in iteritems(self.state.type_map[Car])}
        futures_lights = [(o, o.get_future_color()) for k, o in iteritems(self.state.type_map[TrafficLight])]
        futures_crosswalks = [(o, o.get_future_color()) for k, o in iteritems(self.state.type_map[CrossWalkLight])]
        futures_peds = {k:o.get_future_shape() for k, o in iteritems(self.state.type_map[Pedestrian])}
        buffered_objs = {k: o.shapely_obj.buffer(10) for k, o in iteritems(self.state.type_map[Car])}
        keys = list(futures.keys())
        ped_keys = list(futures_peds.keys())

        solver = pywrapcp.Solver("FLUIDS Background CSP")

        var_map = {}

        for k in futures:
            var = solver.IntVar(-1, 1, str(k))
            var_map[k] = var

        for k in futures_peds:
            var = solver.IntVar(0, 1, str(k))
            var_map[k] = var
        fast_map = {}
        for k1x in range(len(keys)):
            k1 = keys[k1x]
            k1v = var_map[k1]
            car1 = self.state.objects[k1]
            for k2x in range(k1x + 1, len(keys)):
                k2 = keys[k2x]
                k2v = var_map[k2]
                car2 = self.state.objects[k2]

                might_collide = futures[k1].intersects(futures[k2])
                if might_collide:
                    f1 = not futures[k2].intersects(buffered_objs[k1])
                    f2 = not futures[k1].intersects(buffered_objs[k2])
                    solver.Add(k1v + k2v < 2)
                    if not f1:
                        solver.Add((k2v == 1) == False)
                    if not f2:
                        solver.Add((k1v == 1) == False)
            for k2x in range(len(ped_keys)):
                k2 = ped_keys[k2x]
                k2v = var_map[k2]
                ped2 = self.state.objects[k2]
                might_collide = futures[k1].intersects(futures_peds[k2])
                if might_collide:
                    f1 = not futures_peds[k2].intersects(buffered_objs[k1])
                    f2 = not futures[k1].intersects(ped2.shapely_obj)
                    solver.Add(k1v + k2v < 2)
                    if not f1:
                        solver.Add((k2v == 1) == False)
                    if not f2:
                        solver.Add((k1v == 1) == False)
            for fl, flc in futures_lights:
                if flc == "red" and futures[k1].intersects(fl.shapely_obj) and not car1.intersects(fl):
                    solver.Add(k1v == 0)
        for k1x in range(len(ped_keys)):
            k1 = ped_keys[k1x]
            ped1 = self.state.objects[k1]
            for fl, flc in futures_crosswalks:
                if abs(ped1.angle - fl.angle) < np.pi / 2:
                    if flc == "red" and ped1.intersects(fl):
                        solver.Add(k1v == 0)


        db = solver.Phase(sorted([v for k,v in iteritems(var_map)]), solver.CHOOSE_FIRST_UNBOUND, solver.ASSIGN_MAX_VALUE)
        solver.NewSearch(db)

        solver.NextSolution()
        actions = {}
        for k, v in iteritems(var_map):
            if k in self.state.type_map[Car]:

                    actions[k] = VelocityAction(v.Value()*3)

            elif k in self.state.type_map[Pedestrian]:

                    actions[k] = v.Value()


        self.next_actions = actions


    def run_time(self):
        fluids_assert(self.state, "run_time called without setting the state")
        return self.state.time
