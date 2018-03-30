Examples
=========


Specifying An Enviroment with JSON Config Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This introduction will show you how to use the config file to specify an enviroment. First we need to specify how many cars we can control and how many background cars are in the enviroment. This can be done by editing the following JSON values in the config folder. 

::

   "agents":{
        "controlled_cars":1,
        "background_cars":3,
        ...}
    },

The values are currently set to control one car and allow for three background cars. The next thing we need to decide is what action space our agent operates at and what state space it recieves. We will select the steering and Q-Lidar state space via the following values: 

::

   "agents":{
        ...
        "action_space":"steering",
        "state_space":"Q-LIDAR",
        ...}
    },

We can then interact with the world as follows:

::

  action = [np.array([0.0,0.0])]

  env = uds.UrbanDrivingEnv(data)

  obs,reward,done,info_dict = env.step(action)

In the above code, we apply zero control in steering acceleration to our car and recieve a Q-Lidar observation. We additionally recieve a reward, which tells us if we crashed our not. 

:download:`Download <../../examples/setup_tutorial.py>`




Using Supervisors in FLUIDS
^^^^^^^^^^^^^^^^^^^^^^^^^^^
This introduction will show you how to use the config file to specify an enviroment. First we need to specify how many cars we can control and how many background cars are in the enviroment. This can be done by editing the following JSON values in the config folder. 

::

   "agents":{
        "controlled_cars":1,
        "background_cars":3,
        ...}
    },

The values are currently set to control one car and allow for three background cars. The next thing we need to decide is what action space our agent operates at and what state space it recieves. We will select the steering and Q-Lidar state space via the following values: 

::

   "agents":{
        ...
        "action_space":"steering",
        "state_space":"Q-LIDAR",
        ...}
    },

We can then interact with the world as follows:

::

  action = [np.array([0.0,0.0])]

  env = uds.UrbanDrivingEnv(data)

  obs,reward,done,info_dict = env.step(action)

In the above code, we apply zero control in steering acceleration to our car and recieve a Q-Lidar observation. We additionally recieve a reward, which tells us if we crashed our not. 

:download:`Download <../../examples/state_design_tutorial.py>`


.. _`Ray`: http://ray.readthedocs.io/en/latest/
