# Urban Driving Simulator
This repository contains a rudimentary driving simulator for autonomous driving in urban environments. The package implements a OpenAI Gym environment describing a city scene with cars and pedestrians.

This package is substantially modified from http://github.com/WesleyHsieh/gym-driving.

Currently under development.

## Usage
See test.py.

```
import gym
import gym_urbandriving as uds
from gym_urbandriving.assets import Terrain, Lane, Street,
                                    Sidewalk, KinematicCar, Pedestrian
from gym_urbandriving.agents import KeyboardAgent


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
    init_state.dynamic_objects = [KinematicCar(500, 100, angle=-92, vel=5),
                                  KinematicCar(100, 500, angle=0, vel=5),
                                  Pedestrian(100, 370, vel=2)
    ]
```

First we initialize a `PyGameVisualizer` and design our scene as a `PositionState`. Arbitrarily complex scenes can be designed here. 

```
env = uds.UrbanDrivingEnv(visualizer=vis,init_state=init_state)
```
The `UrbanDrivingEnv` adheres to OpenAI Gym's Env API. This environment will handle processing agent actions and updating the environment state. 

```
state= init_state
agent = KeyboardAgent()
action = None
while(True):
    action = agent.eval_policy(state)
    state, reward, done = env._step(action)
    env._render()
    if done:
        print("done")
        env._reset()
```
We run the simulation here. `KeyboardAgent` responds to arrow key commands.
