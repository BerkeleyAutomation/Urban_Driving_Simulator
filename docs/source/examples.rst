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
Designing a state is very simple in UDS. To design a custom state, simply inherit from ``PositionState``, implement your own array of ``static_objects`` and define your own ``randomize()`` function.

First, create a custom state class that inherits from ``PositionState``. Let's also set up the render cycle.

::

   import gym_urbandriving as uds
   from gym_urbandriving.state import PositionState
   from gym_urbandriving.agents import NullAgent
   from gym_urbandriving.assets import Car, Terrain, Street, Lane, Sidewalk

   class CustomState(PositionState):
      static_objects = []

   vis = uds.PyGameVisualizer((800, 800))
   init_state = CustomState()
   env = uds.UrbanDrivingEnv(init_state=init_state,
                             visualizer=vis,
                             randomize=True)

   while(True):
      env._render()

Now, running this script should generate a blank screen.

.. image:: blank.png

Lets add the streets to our state now. Streets are composed of ``Lane`` and ``Street`` objects. ``Lane`` objects are associated with directionality, so use these to construct the two sides of a road. ``Street`` objects should be used at intersections, where cars can travel in any direction. Lets build a three-way intersection between a four lane road and a two lane road. Place down the four lane road first. For rectangular objects, the arguments are the coordinates of the centroid, the height and width of the object, and then any rotation around the centroid.

::

   class CustomState(PositionState):
      static_objects = [Lane(175, 550, 350, 100, angle=-180),
                        Lane(175, 650, 350, 100, angle=-180),
                        Lane(175, 750, 350, 100),
                        Lane(175, 850, 350, 100),
                        Lane(825, 550, 350, 100, angle=-180),
                        Lane(825, 650, 350, 100, angle=-180),
                        Lane(825, 750, 350, 100),
                        Lane(825, 850, 350, 100),
                        Street(500, 700, 300, 400),]


.. image:: custom1.png

Notice how the angle of the lanes is manipulated so the road has proper directionality. Next, let's add the third road and some sidewalks. Sidewalks have no directionality, so we can just place them down directly.

::

   class CustomState(PositionState):
      static_objects = [Lane(175, 550, 350, 100, angle=-180),
                        Lane(175, 650, 350, 100, angle=-180),
                        Lane(175, 750, 350, 100),
                        Lane(175, 850, 350, 100),
                        Lane(825, 550, 350, 100, angle=-180),
                        Lane(825, 650, 350, 100, angle=-180),
                        Lane(825, 750, 350, 100),
                        Lane(825, 850, 350, 100),
                        Street(500, 700, 300, 400),
                        Lane(450, 250, 500, 100, angle=-90),
                        Lane(550, 250, 500, 100, angle=90),
                        Sidewalk(200, 475, 400, 50),
                        Sidewalk(800, 475, 400, 50)]

.. image:: custom2.png

We are almost done. All thats left is to fill in the empty blocks with ``Terrain`` objects and write our own ``randomize`` function. The easiest way is to use the ``Lane`` objects' builtin ``generate_car`` and the ``Sidewalk`` objects' builtin ``generate_man`` functions. When generating objects, you need to check if they collide with other randomly generated objects

::

  class CustomState(PositionState):
      static_objects = [Lane(175, 550, 350, 100, angle=-180),
                        Lane(175, 650, 350, 100, angle=-180),
                        Lane(175, 750, 350, 100),
                        Lane(175, 850, 350, 100),
                        Lane(825, 550, 350, 100, angle=-180),
                        Lane(825, 650, 350, 100, angle=-180),
                        Lane(825, 750, 350, 100),
                        Lane(825, 850, 350, 100),
                        Street(500, 700, 300, 400),
                        Lane(450, 250, 500, 100, angle=-90),
                        Lane(550, 250, 500, 100, angle=90),
                        Sidewalk(200, 475, 400, 50),
                        Sidewalk(800, 475, 400, 50),
                        Terrain(200, 225, 400, 450),
                        Terrain(800, 225, 400, 450),
                        Terrain(500, 950, 1000, 100)]

      def randomize(self):
            self.dynamic_objects = []
            lane_objs = [obj for obj in self.static_objects if type(obj) == Lane]
            sidewalk_objs = [obj for obj in self.static_objects if type(obj) == Sidewalk]

            for i in range(3):
              car = random.choice(lane_objs).generate_car()
              if not any([car.collides(obj) for obj in self.static_objects + self.dynamic_objects]):
                  self.dynamic_objects.append(car)
            for i in range(2):
              man = random.choice(sidewalk_objs).generate_man()
              if not any([man.collides(obj) for obj in self.static_objects + self.dynamic_objects]):
                  self.dynamic_objects.append(man)

Now, you should see the following image (or something similar) when running this script.

.. image:: custom3.png

Imitation Learning
^^^^^^^^^^^^^^^^^^

Finally, we will walk through training an Imitation Learning Agent to mimic a Tree Search Agent. First, we need to set up an environment in which to collect data.

::

    vis = uds.PyGameVisualizer((800, 800))
    init_state = uds.state.SimpleIntersectionState(ncars=2, nped=0)

    env = uds.UrbanDrivingEnv(init_state=init_state,
                              visualizer=vis,
                              agent_mappings={Car:AccelAgent},
                              max_time=200,

                              randomize=True,
                              use_ray=True)

    env._render()
    state = env.current_state
    agent = TreeSearchAgent()

We will also need arrays to store the state and actions taken by the agent

::

    saved_states = []
    saved_actions = []


As well as a function that will turn our state into a vector form that is easier to load later.

::

   def vectorize_state(state):
       res = []
       for obj in state.dynamic_objects:
           res.extend([obj.x, obj.y, obj.vel, obj.angle])
       return res

We can now save the vectorized state every time step, and the actions taken by each agent, which we obtain with ``info_dict["saved_actions"]``.

::

        action = agent.eval_policy(deepcopy(state))
        saved_states.append(vectorize_state(state))
        start_time = time.time()
        state, reward, done, info_dict = env._step(action)
        saved_actions.append(info_dict["saved_actions"])

And after a demonstration is over, we can reset our env, our saved states and actions, and dump our data to a pickle file.

::

   if done:
         env._reset()
         state = env.current_state

         # reset agent state
         agent.waypoints = None
         agent.actions = None

         pickle.dump((saved_states, saved_actions),open("data/"+str(np.random.random())+"dump.data", "wb+"))

         saved_states = []
         saved_actions = []


All of this is included in ``examples/collect_data.py`` and running this file should start to generate pickle files in the ``./data`` directory.

To then learn from this data, we use a random decision forest. This is currently implemented in ``examples/learn_model.py``.

The most important lines are

::

  model = RandomForestClassifier(n_estimators=10, criterion='gini', max_features=None, max_depth=15)
  model.fit(train_X, train_y)

Here, we make a RandomForestClassifier and fit it to the data. In general, any scipy classifier will work.

Finally, we can test our model in the environment again, only this time we set our agent to be a ModelAgent.

::

    vis = uds.PyGameVisualizer((800, 800))
    init_state = uds.state.SimpleIntersectionState(ncars=2, nped=0)

    env = uds.UrbanDrivingEnv(init_state=init_state,
                              visualizer=vis,
                              agent_mappings={Car:AccelAgent},
                              max_time=200,
                              randomize=True,
                              use_ray=True)

    env._render()
    state = init_state
    agent = ModelAgent()


The Model Agent will load the model that we learned and saved, and apply the appropriate action.

::

    def eval_policy(self, state):
        return self.model.predict(np.array([self.vectorize_state(state)]))[0]


It must also vectorize the state the same way our data collector does.
