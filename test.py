import gym
import gym_urbandriving as uds
import cProfile
from gym_urbandriving.assets import Terrain, Lane, Street, Sidewalk, KinematicCar, Pedestrian, Car
from gym_urbandriving.agents import KeyboardAgent, SimpleAvoidanceAgent, AccelAgent, NullAgent

import numpy as np

def randomizer(state):
    state.dynamic_objects = []
    state.static_objects = [Terrain(175, 175, 350, 350),
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
    car_pos = [(450, 50, -90), (450, 200, -90), (450, 350, -90),
               (550, 950, 90), (550, 800, 90), (550, 650, 90),
               (50, 550, 0), (200, 550, 0), (350, 550, 0),
               (950, 450, -180), (800, 450, -180), (650, 450, -180),
    ]
    ped_pos = [(350, 370, 0), (300, 370, 0), (250, 370, 0),
               (350, 630, 0), (300, 630, 0), (250, 630, 0),
               (650, 370, -180), (700, 370, -180), (750, 370, -180),
               (650, 630, -180), (700, 630, -180), (750, 630, -180),
               (370, 350, -90), (370, 300, -90), (370, 250, -90),
               (630, 350, -90), (630, 300, -90), (630, 250, -90),
               (370, 650, 90), (370, 700, 90), (370, 750, 90),
               (630, 650, 90), (630, 700, 90), (630, 750, 90),
    ]
    for i in range(6):
        a = np.random.uniform()
        if a > 0.7:
            b = np.random.random_integers(0, len(ped_pos) - 1)
            x, y, angle = ped_pos[b]
            vel = np.random.uniform(0, 2)
            ped_pos.pop(b)
            state.dynamic_objects.append(Pedestrian(x, y, angle=angle, vel=vel))
        else:
            b = np.random.random_integers(0, len(car_pos) - 1)
            x, y, angle = car_pos[b]
            vel = np.random.uniform(0, 20)
            car_pos.pop(b)
            state.dynamic_objects.append(KinematicCar(x, y, angle=angle, vel=vel))
    return state

def f():

    vis = uds.PyGameVisualizer((800, 800))
    init_state = uds.state.PositionState()
    init_state = randomizer(init_state)

    env = uds.UrbanDrivingEnv(init_state=init_state,
                              visualizer=vis,
                              bgagent=AccelAgent,
                              max_time=100,
                              randomizer=randomizer)
    state = init_state
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
