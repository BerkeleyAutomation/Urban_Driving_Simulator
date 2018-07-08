FLUIDS Core API
===============

Simulator Interface
^^^^^^^^^^^^^^^^^^^

The most powerful way to interact with fluids is to create a ``fluids.FluidSim`` object. This object creates the environment, sets up all cars, and pedestrians, and controls background objects in the scene. The initialization arguments to this object control the parameters of the generated environment

.. autoclass:: fluids.FluidSim
   :members: get_control_keys, step, get_observations

Action Types
^^^^^^^^^^^^
FLUIDS supports four action types. All action types are acceptable for ``FluidSim.step``.

.. autoclass:: fluids.actions.KeyboardAction
.. autoclass:: fluids.actions.SteeringAction
.. autoclass:: fluids.actions.VelocityAction
.. autoclass:: fluids.actions.LastValidAction

Observation Types
^^^^^^^^^^^^^^^^^
FLUIDS supports two observation types currently, a BirdsEye observation and a Grid observation.

.. autoclass:: fluids.obs.FluidsObs
   :members: get_array
.. autoclass:: fluids.obs.GridObservation
.. autoclass:: fluids.obs.BirdsEyeObservation

Command Line Interface
^^^^^^^^^^^^^^^^^^^^^^
FLUIDS also provides a command line interface for visualizing the environment running without a user agent. Controlled agents in this mode are controllable by keyboard only.

::

   python3 -m fluids

Run with -h flag to see arguments

::

   >>> python3 -m fluids -h
   usage: __main__.py [-h] [-b N] [-c N] [-p N] [-v N] [-o str] [--state file]

   FLUIDS First Order Lightweight Urban Intersection Driving Simulator

   optional arguments:
   -h, --help    show this help message and exit
   -b N          Number of background cars
   -c N          Number of controlled cars
   -p N          Number of background pedestrians
   -v N          Visualization level
   -o str        Observation type
   --state file  Layout file for state generation

   Keyboard commands for when visualizer is running:
    .            Increases debug visualization
    ,            Decreases debug visualization
    o            Switches observation type
