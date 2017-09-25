import gym
import gym_urbandriving as uds
import cProfile
from gym_urbandriving.assets import *

def f():
    
    vis = uds.PyGameVisualizer((800, 800))
    init_state = uds.state.PositionState()
    init_state.static_objects = [Terrain(175, 175, 350, 350),
                  Terrain(825, 175, 350, 350),
                  Terrain(175, 825, 350, 350),
                  Terrain(825, 825, 350, 350),
                  Street(500, 500, 200, 1000),
                  Street(500, 500, 1000, 200),
                  Sidewalk(200, 375, 400, 50),
                  Sidewalk(200, 625, 400, 50),
                  Sidewalk(800, 375, 400, 50),
                  Sidewalk(800, 625, 400, 50),
                  Sidewalk(375, 175, 50, 350),
                  Sidewalk(625, 175, 50, 350),
                  Sidewalk(375, 825, 50, 350),
                  Sidewalk(625, 825, 50, 350),
                ]
    init_state.dynamic_objects = [Car(500, 100, angle=-92, vel=5),
                                   KinematicCar(100, 500, angle=14, vel=5),
                                   Pedestrian(100, 370, vel=2)
                                 ]

    env = uds.UrbanDrivingEnv(visualizer=vis,init_state=init_state)
        
    while(True):
        state, reward, done = env._step(None)
        env._render()
        if done:
            print("done")
            env._reset()

cProfile.run('f()', 'stats')
