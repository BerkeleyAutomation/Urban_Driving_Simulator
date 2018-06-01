Examples
=========

This tutorial will walk you though many of the features of FLUIDs to run an intersection simulation with multiple user controlled cars, background cars, pedestrians, and traffic lights. A link ot the final code is below:

:download:`Download <../../examples/test.py>`

Configuring the Environment
---------------------------
The environment and agent configuration in FLUIDS is controlled by JSON configuration files. 

::

   "environment":{
       "state":"four_way_intersection",
       "visualize": true,
       "visualize_lidar": true,
       "max_time": 500
   },

The "state" flag specifies the layout of the roads, terrain, and sidewalks in the scene by pointing the simulator to a scene description JSON. We currently package only the four way intersection.

The "visualize" and "visualize_lidar" flags enable the graphical display, which is optional.

The "max_time" field specifies the maximum number of ticks the simulation will run before resetting. This is useful for performing many roll-outs back-to-back.

::

   "agents":{
      "controlled_cars":1,
      "background_cars":3,
      "action_space":"steering",
      "state_space":"Q-LIDAR",
      "state_space_config":{
         "goal_position":false,
         "noise":0,
         "omission_prob":0
      },
      "bg_state_space_config":{
         "noise":0,
         "omission_prob":0
      },
      "use_traffic_lights":true,
      "number_of_pedestrians":0,
      "agent_mappings":{
         "Car":"PlanningPursuitAgent",
         "TrafficLight":"TrafficLightAgent",
         "CrosswalkLight":"CrosswalkLightAgent",
         "Pedestrian":"PedestrianAgent"
      }
    },

There's a lot here, but most of it is self-explanatory. Here, we specify 1 controlled car with user-defined controls, and 3 background cars controlled by our supervisor. The "action_space" of our controlled car will be the steering control. This can be configured to multiple levels of the self-driving hierarchy. The "state_space" and "state_space_config" fields configure the state representation available to the user agent. Here we use our "quasi-lidar" representation.

We create the state with traffic lights and pedestrians. The "agent_mappings" field marks what types of agents are controlling every type of background object.

Running the Environment
--------------------------
The basic evaluation loop is very simple. We initialize the environment with the config file. In the simulation loop, we repeatedly step forward through the environment, receive observations, and provide new actions for all controlled cars in the scene.

::

   import gym
   import gym_urbandriving as uds
   from gym_urbandriving.actions import SteeringAction
   import numpy as np
   import json

   config = json.load(open('configs/default_config.json'))
   env = uds.UrbanDrivingEnv(config_data=config)

   env._reset()
   env._render()
   obs = env.get_initial_observations()
   action = SteeringAction(0, 0)

   while(True):
       obs, reward, done, info_dict = env._step([action])
       env._render()
       if done:
           print("done")
           env._reset()
           obs = env.get_initial_observations()

Here we step forward through the simulation until either there is a collision, or the max time is reached. We provide a SteeringAction because the environment was configured such that user cars received SteeringActions. The actions are provided in an array to support multiple controlled vehicles.

Now we connect agents to the controlled cars. For this test, we use keyboard agents.

::
   
   from gym_urbandriving.agents import KeyboardAgent
   agent = KeyboardAgent()
   while(True):
       action = agent.eval_policy(obs[0])
       obs, reward, done, info_dict = env._step([action])
       env._render()
       if done:
           print("done")
           env._reset()
           obs = env.get_initial_observations()

Notice that the observations returned are an array, one for each controlled car. The observation is specified in the config file. For this example, Q-LIDAR observations are used. Q-LIDAR represents a set of observations similar to what a self-driving car might receive from camera and LIDAR sensors.

Using Pedestrians
^^^^^^^^^^^^^^^^^
FLUIDS will also simulate pedestrian behavior with cross-walk lights. Adjust the flag in the configuration, which is loaded as a Python dictionary.

::

   config['agents']["number_of_pedestrians"]:4

Using Neural Background Agents
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To improve performance of background agents when many of them are in the scene, their agents can be configured as NeuralPursuitAgents. Adjust the "agent_mappings" flag in the configuration.

::

   config['agents']['agent_mappings']['Car'] = 'NeuralPursuitAgent'

Using a Steering Supervisor
^^^^^^^^^^^^^^^^^^^^^^^^^^^
FLUIDS is packaged with supervisor agents at several levels of the controls hierarchy for a self-driving car. First we replace the KeyboardAgent with a SteeringSupervisor. Since the steering supervisor expects access to the full state, we specify this in the config file.

::

   config['agents']['state_space'] = 'raw'

::

   from gym_urbandriving.agents import SteeringSupervisor
   agent = SteeringSupervisor()
   while(True):
       action = agent.eval_policy(obs[0])
       obs, reward, done, info_dict = env._step([action])
       env._render()

Using a Velocity Supervisor
^^^^^^^^^^^^^^^^^^^^^^^^^^^
While the steering supervisor provides full steering and acceleration controls to the car, FLUIDS can also provide an input to one level of the hierarchy. Here we demonstrate the velocity supervisor, which sets the velocity of the car along a path generated by a path planner.

::

   config['agents']['state_space'] = 'raw'
   config['agents']['action_space'] = 'velocity'

::

   from gym_urbandriving.agents import VelocitySupervisor
   agent = VelocitySupervisor()
   while(True):
       action = agent.eval_policy(obs[0])
       obs, reward, done, info_dict = env._step([action])
       env._render()



Designing Custom Intersections
------------------------------
Custom intersections are described in gym_urbandriving/states/configs. A custom intersection is a .JSON file.

::

   {
      "static_objects": [
        { "type":"Terrain" , "x":175, "y":175, "xdim":350, "ydim":350 },
        { "type":"Lane"    , "x":200, "y":450, "xdim":400, "ydim":100, "angle_deg":-180 },
        { "type":"Street"  , "x":500, "y":500, "xdim":200, "ydim":200 },
        { "type":"Sidewalk", "x":625, "y":825, "xdim":350, "ydim":50,  "angle_deg":90 }
        ],
      "car_start_lanes": [
        { "x":450, "y":200, "xdim":400, "ydim":100, "angle_deg":-90 },
        ],
      "traffic_lights": [
        { "x": 600, "y": 450, "init_color":"green", "angle_deg":0},
        ],
      "crosswalk_lights": [
        { "x": 610, "y": 625, "init_color":"white", "angle_deg":-180 },
        ],
      "goal_states": [
        { "x":550, "y":100, "vel":2, "angle_deg":90 },
        ]
   }

"static_objects" describe the position of all fixed objects in the scene. Terrain blocks are impassable to vehicles and pedestrians. Lane blocks represent areas where cars may only travel in a certain direction. Street and Sidewalk blocks represent areas where vehicles and pedestrians can move in any direction.

"car_start_lanes" describe the zones in which cars are randomly placed in scene generation.

"traffic_lights" and "crosswalk_lights" describe initial positions and states of those objects.

"goal_states" describe possible destination positions for all cars.
