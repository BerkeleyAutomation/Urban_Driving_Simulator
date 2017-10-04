import gym
import gym_urbandriving as uds
import cProfile
from gym_urbandriving.assets import Terrain, Lane, Street, Sidewalk, KinematicCar, Pedestrian, Car
from gym_urbandriving.agents import KeyboardAgent, SimpleAvoidanceAgent, AccelAgent
from threading import Thread

def f():

    vis = uds.PyGameVisualizer((800, 800))
    init_state = uds.state.PositionState()
    init_state.static_objects = [Terrain(175, 175, 350, 350),
                                 Terrain(825, 175, 350, 350),
                                 Terrain(175, 825, 350, 350),
                                 Terrain(825, 825, 350, 350),
                                 Lane(200, 450, 400, 100, angle=-180),
                                 Lane(200, 550, 400, 100),
                                 Lane(200, 450, 400, 100, angle=-180),
                                 Lane(200, 550, 400, 100),
                                 Lane(800, 450, 400, 100, angle=-180),
                                 Lane(800, 550, 400, 100),
                                 Lane(450, 200, 400, 100, angle=-90),
                                 Lane(550, 200, 400, 100, angle=90),
                                 Lane(450, 800, 400, 100, angle=-90),
                                 Lane(550, 800, 400, 100, angle=90),
                                 Street(500, 500, 200, 200),
                                 Sidewalk(200, 375, 400, 50),
                                 Sidewalk(200, 625, 400, 50),
                                 Sidewalk(800, 375, 400, 50),
                                 Sidewalk(800, 625, 400, 50),
                                 Sidewalk(375, 175, 50, 350),
                                 Sidewalk(625, 175, 50, 350),
                                 Sidewalk(375, 825, 50, 350),
                                 Sidewalk(625, 825, 50, 350),
    ]
    init_state.dynamic_objects = [KinematicCar(450, 100, angle=-90, vel=10),
                                  KinematicCar(50, 550, angle=0, vel=10),
                                  KinematicCar(250, 550, angle=0, vel=10),
                                  KinematicCar(900, 450, angle=-180, vel=10),
                                  KinematicCar(550, 900, angle=-270, vel=0),
                                  Pedestrian(350, 370, vel=2)
    ]

    env = uds.UrbanDrivingEnv(visualizer=vis,init_state=init_state,
                              bgagent=AccelAgent,
                              max_time=500)
    state= init_state
    agent = AccelAgent()
    action = None
    def job():
        env._render()
    while(True):
        action = agent.eval_policy(state)
        state, reward, done, info_dict = env._step(action)
        env._render()
        if done:
            print("done")
            print(info_dict["dynamic_collisions"])
            env._reset()

cProfile.run('f()', 'stats')
