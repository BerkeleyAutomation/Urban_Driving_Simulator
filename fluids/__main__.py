import fluids



simulator = fluids.FluidSim(visualization_level=4,        # How much debug visualization you want to enable. Set to 0 for no vis
                            background_cars=10,           # How many background cars
                            controlled_cars=1,            # How many cars to control. Set to 0 for background cars only
                            fps=0,                        # If set to non 0, caps the FPS. Target is 30
                            obs_space=fluids.OBS_BIRDSEYE,# OBS_BIRDSEYE, OBS_GRID, or OBS_NONE
                            background_control=fluids.BACKGROUND_CSP) 
while True:
    obs, rew = simulator.step({})
