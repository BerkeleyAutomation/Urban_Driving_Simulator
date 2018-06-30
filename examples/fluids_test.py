import fluids
import pygame
import numpy as np

simulator = fluids.FluidSim(visualization_level=4,
                            background_cars=10,
                            controlled_cars=1,
                            fps=0,
                            obs_space=fluids.OBS_NONE,
                            background_control=fluids.BACKGROUND_CSP)

controlled_keys = simulator.get_control_keys()

while True:
    actions = {k:fluids.SteeringAction(0, 0) for k in controlled_keys}
    simulator.step(actions)
    a = 1
