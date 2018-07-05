FLUIDS Gym Env API
==================

The FLUIDS Gym Environment provides a simpler common interface to the FLUIDS simulator that is compatible with general agents following the Gym API.


::

   import gym
   import gym_fluids

   env = gym.make("fluids-v2")


The current Gym environment supports 1 controlled car interacting with 10 background cars and 5 pedestrians. The action space is a ``[steering, acc]`` pair. The observation space is a ``500 x 500`` RGB image from the car's perspective. A reward function considering collisions and distance traveled along the given trajectory is provided.
