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

:download:`Download <../../examples/json_setup.py>`




Using Supervisors in FLUIDS
^^^^^^^^^^^^^^^^^^^^^^^^^^^
FLUIDS come with prebuilt in supervisors that can be used to collect data or as a baseline. 
In this example we will control two cars with two supervisors. We can change the number of control cars by editing the config file. 

::

   "agents":{
        "controlled_cars":2,
        "background_cars":3,
        ...}
    },

We can then declare supervisors as follows:

::

   supervisors = []

  supervisors.append(SteeringSupervisor(agent_num = 0))
  supervisors.append(SteeringSupervisor(agent_num = 1))

The above code shows the decleration of two supervisors that provide actions on the steering level of supervision. They are each indexed by their agent_num. Note that other supervisors exists such as velocity and trajecotry for the different levels of the hierarchy. 

::

  actions = []

  env = uds.UrbanDrivingEnv(data)
  current_global_state  = env.current_state


  for t in range(5): 
      for supervisor in supervisors:
      actions.append(supervisor.eval_policy(state))

      obs,reward,done,info_dict = env.step(actions)
      current_global_state = env.current_state

      actions = []

In the above code, we have the supervisors interact with the world for five timesteps. At each timestep the superivosr is given the global state of the world and makes a decision of what action to take. Then the list of specified actions is fed into the enviroment. 

:download:`Download <../../examples/state_design_tutorial.py>`


.. _`Ray`: http://ray.readthedocs.io/en/latest/
