import gym
import gym_urbandriving as uds
import cProfile
from gym_urbandriving.assets import Terrain, Lane, Street, Sidewalk, KinematicCar, Pedestrian, Car
from gym_urbandriving.agents import ModelAgent, KeyboardAgent, SimpleAvoidanceAgent, AccelAgent, NullAgent

import numpy as np
import pickle
import time

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
    car_pos_1 = [(450, 200, -90), (450, 350, -90)]
    car_pos_2 = [(550, 700, 90), (550, 550, 90)]
    car_pos_3 = [(200, 550, 0), (350, 550, 0)]
    car_pos_4 = [(700, 450, -180), (550, 450, -180)]
    
    ped_pos = [(350, 370, 0), (300, 370, 0), (250, 370, 0),
               (350, 630, 0), (300, 630, 0), (250, 630, 0),
               (650, 370, -180), (700, 370, -180), (750, 370, -180),
               (650, 630, -180), (700, 630, -180), (750, 630, -180),
               (370, 350, -90), (370, 300, -90), (370, 250, -90),
               (630, 350, -90), (630, 300, -90), (630, 250, -90),
               (370, 650, 90), (370, 700, 90), (370, 750, 90),
               (630, 650, 90), (630, 700, 90), (630, 750, 90),
    ]
    
    for car_pos in [car_pos_3, car_pos_4]:
        a = np.random.uniform()
        if a>.5:
            x, y, angle = car_pos[0]
            vel = np.random.uniform(0, 10)
            state.dynamic_objects.append(KinematicCar(x+25*np.random.normal(), y, angle=angle, vel=vel))
        else:
            x, y, angle = car_pos[1]
            vel = np.random.uniform(0, 10)
            state.dynamic_objects.append(KinematicCar(x+25*np.random.normal(), y, angle=angle, vel=vel))
    for car_pos in [ car_pos_1, car_pos_2]:
        a = np.random.uniform()
        if a>.5:
            x, y, angle = car_pos[0]
            vel = np.random.uniform(0, 10)
            state.dynamic_objects.append(KinematicCar(x, y+25*np.random.normal(), angle=angle, vel=vel))
        else:
            x, y, angle = car_pos[1]
            vel = np.random.uniform(0, 10)
            state.dynamic_objects.append(KinematicCar(x, y+25*np.random.normal(), angle=angle, vel=vel))

    return state


def vectorize_state(state):
    state_vec = []
    for obj in state.dynamic_objects:
        state_vec.append(np.array([(obj.x-500)/500, (obj.y-500)/500, (obj.vel-10)/10]))
    return state_vec

def f():
    saved_states = []
    saved_actions = []
    accs = 0
    totalticks = 0
    num_exps = 0
    start_time = time.time()

    vis = uds.PyGameVisualizer((800, 800))
    init_state = uds.state.PositionState()
    init_state = randomizer(init_state)

    env = uds.UrbanDrivingEnv(init_state=init_state,
                              visualizer=vis,
                              bgagent=ModelAgent,
                              max_time=100,
                              randomizer=randomizer)
    state = init_state
    agent = ModelAgent()
    reset_counter = 0
    
    action = None
    def job():
        env._render()
    while(True):
        action = agent.eval_policy(state)
        saved_states.append(vectorize_state(state))
        state, reward, done, info_dict = env._step(action)
        #print(info_dict["saved_actions"])
        saved_actions.append(info_dict["saved_actions"])
        
        if info_dict["saved_actions"] == [(0, 1), (0, 1), (0, 1), (0, 1)]:
            reset_counter+=1
        else:
            reset_counter = 0

        totalticks += 1
        env._render()
        
        if done or reset_counter >10:
            reset_counter = -10
            """
            if type(agent) is AccelAgent:
                print(saved_states[0])
                pickle.dump((saved_states, saved_actions),open("data/"+str(np.random.random())+"dump.data", "wb+"))
            """
            #print("done")
            print((time.time()-start_time)/totalticks, totalticks)
            #print(info_dict["dynamic_collisions"])
            
            if type(agent) is ModelAgent:
              accs += info_dict["predict_accuracy"]
              #print(accs/totalticks)
              num_exps += 1
              if num_exps == 131:
                  exit

             

            env._reset()
            saved_states = []
            saved_actions = []

cProfile.run('f()', 'stats')
