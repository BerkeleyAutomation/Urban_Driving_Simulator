import gym
import gym_urbandriving as uds
import cProfile
import time
import numpy as np
import pickle
import skimage.transform
import cv2

from gym_urbandriving.agents import KeyboardAgent, AccelAgent, NullAgent, TrafficLightAgent, RRTAgent
from gym_urbandriving.assets import Car, TrafficLight


# Four corners of the interection, hard-coded in camera space
corners = np.array([[765, 385],
                    [483, 470],
                    [1135, 565],
                    [1195, 425]])

# Four corners of the intersection, hard-coded in transformed space
st_corners = np.array([[400, 400],
                       [400, 600],
                       [600, 600],
                       [600, 400]])
tf_mat = skimage.transform.ProjectiveTransform()
tf_mat.estimate(st_corners, corners)

def transform_trajectory(trajectory):
    tf_traj = []
    for x, y, t in trajectory:
        x, y = x * 1280, y * 720
        tx, ty = tf_mat.inverse(np.array((x, y)))[0]
        tx = tx * 1.04
        ty = ty * 1.17
        tf_traj.append((tx, ty, t))
    return tf_traj

def get_single_trajectory(trajectories, index, scale=(1000, 1000)):
    traj = []
    c = None
    for t, frame in enumerate(trajectories):
        for x, y, cls, i in frame:
            if i == index:
                traj.append((x, y, t))
                c = cls
    return traj, c
def f():
    trajectories = pickle.load(open("/home/jerry/Documents/drive/Projects/uds/albertacam/test/trajectories.pkl"))



    
    # Instantiate a PyGame Visualizer of size 800x800
    vis = uds.PyGameVisualizer((800, 800))

    # Create a simple-intersection state, with 4 cars, no pedestrians, and traffic lights
    init_state = uds.state.SimpleIntersectionState(ncars=1, nped=0, traffic_lights=True)

    # Create the world environment initialized to the starting state
    # Specify the max time the environment will run to 500
    # Randomize the environment when env._reset() is called
    # Specify what types of agents will control cars and traffic lights
    # Use ray for multiagent parallelism
    env = uds.UrbanDrivingEnv(init_state=init_state,
                              visualizer=vis,
                              max_time=500,
                              randomize=False,
                              agent_mappings={Car:NullAgent,
                                              TrafficLight:TrafficLightAgent},
    )
    init_state.dynamic_objects = []
    agent = RRTAgent()
    for i in [0, 3, 5, 7]:
        trajectory, cls = get_single_trajectory(trajectories, i)
        if not len(trajectory):
            break
        tf_trajectory = transform_trajectory(trajectory)
        init_state.dynamic_objects.append(Car(tf_trajectory[0][0], tf_trajectory[0][1], breadcrumbs=tf_trajectory))
    init_state.dynamic_objects[0].angle = np.pi/2
    init_state.dynamic_objects[0].y = 650
    init_state.dynamic_objects[0].x = 535

    init_state.dynamic_objects[1].angle = np.pi/4
    init_state.dynamic_objects[1].y = 500
    init_state.dynamic_objects[1].x = 425

    init_state.dynamic_objects[2].angle = -np.pi/2
    init_state.dynamic_objects[2].y = 350
    init_state.dynamic_objects[2].x = 479

    init_state.dynamic_objects[3].angle = -np.pi/2
    init_state.dynamic_objects[3].y = 260
    init_state.dynamic_objects[3].x = 479

    env._reset(new_state=init_state)
    while (True):
        env._render()

    state = env.current_state

    # while(True):
    #     action = agent.eval_policy(state)
    #     state, reward, done, info_dict = env._step(action)
    #     env._render()
    #     if not state.dynamic_objects[0].breadcrumbs:
    #         break


# Collect profiling data
cProfile.run('f()', 'temp/stats')
