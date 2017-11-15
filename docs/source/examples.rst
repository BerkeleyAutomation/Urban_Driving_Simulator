Examples
=========

Introduction
^^^^^^^^^^^^
This introduction will guide you through running a simple example on the simulator

::

   import gym
   import gym_urbandriving as uds
   from uds.agents import KeyboardAgent, NullAgent
   form uds.state import SimpleIntersectionState
   from uds.assets import Car, Pedestrian
   from uds import UrbanDrivingEnv

   vis = uds.PyGameVisualizer((800, 800))
   init_state = SimpleIntersectionState(ncars=3, nped=2)
   env = UrbanDrivingEnv(init_state=init_state,
                         visualizer=vis
                         max_time=500,
                         randomize=True,
                         agent_mappings={Car:NullAgent,
                                         Pedestrian:NullAgent}
                         )

   env._render()

   
First we create a visualizer window of size 800x800. We use PyGame for visualization

The ``SimpleIntersectionState`` defines a simple four-way intersection. We instantiate
our initial state with 3 cars and 2 pedestrians.

The ``UrbanDrivingEnv`` handles running the simulation and collecting agent actions.
We instantiate it with our initial state and visualizer. ``max_time=500`` tells the
environment to reset after 500 ticks if no crashes occur. ``randomize=True`` makes the
environment call the ``randomize`` function in the ``SimpleIntersectionState``, making the
``SimpleIntersectionState`` reset itself to a random arrangement of 3 cars and 2
pedestrians. We use ``agent_mappings`` to specify what types of agents control background
objects. In this case, we use ``NullAgents``, which take no action.

Next we setup the control and simulation loop

::

   state = init_state
   agent = KeyboardAgent(agent_num=0)
   while (True):
      action = agent.eval_policy(state)
      state, reward, done, info_dict = env._step(action)
      env._render()

      if done:
         env._reset()
         state = env.get_state_copy()

We choose a ``KeyboardAgent`` to control the main car in the scene. Its ``agent_num``
specifies the index of the object it is controlling in the scene. For any agent, calling
``agent.eval_policy(state)`` returns the action the agent would take for the ``agent_num``
object in the state. ``env._step()`` applies the action to the ``0th`` controllable object
in the scene. For every other object, it queries its internal list of agents as specified in
``agent_mappings``. Once every action is collected, ``env_.step`` advances the state and returns.


Designing a State
^^^^^^^^^^^^^^^^^
Designing a state is very simple in UDS. To design a custom state, simply inherit from ``PositionState`` and implement your own array of ``static_objects`` and define your own ``randomize()`` function.

::

   class CustomState(PositionState):
      static_objects = [Terrain(175, 175, 350, 350),
                        Terrain(825, 175, 350, 350),
                        Terrain(175, 825, 350, 350),
                        Terrain(825, 825, 350, 350),
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
                        Sidewalk(625, 825, 50, 350),]

You should place the dynamic objects in the ``randomize()`` function


::
   
      def randomize(self):
         self.dynamic_objects = []
         self.dynamic_objects.append(Car(500, 200))

Imitation Learning
^^^^^^^^^^^^^^^^^^
