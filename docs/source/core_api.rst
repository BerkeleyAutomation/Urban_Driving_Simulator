FLUIDS Core API
===============

Simulator Interface
^^^^^^^^^^^^^^^^^^^

The most powerful way to interact with fluids is to create a ``fluids.FluidSim`` object. This object creates the environment, sets up all cars, and pedestrians, and controls background objects in the scene. The initialization arguments to this object control the parameters of the generated environment

.. autoclass:: fluids.FluidSim
   :members: get_control_keys, step

Action Types
^^^^^^^^^^^^
FLUIDS supports four action types. All action types are acceptable for ``FluidSim.step``.

.. autoclass:: fluids.actions.KeyboardAction
.. autoclass:: fluids.actions.SteeringAction
.. autoclass:: fluids.actions.VelocityAction
.. autoclass:: fluids.actions.LastValidAction


Command Line Interface
^^^^^^^^^^^^^^^^^^^^^^
FLUIDS also provides a command line interface for visualizing the environment running without a user agent. Controlled agents in this mode are controllable by keyboard only.

::

   python3 -m fluids

Run with -h flag to see arguments

::
   
   >>> python3 -m fluids -h
   optional arguments:
   -h, --help           show this help message and exit
   -b N                 Number of background cars
   -c N                 Number of controlled cars
   -p N                 Number of background pedestrians
   -v N                 Visualization level
   --state layout file  Layout file for state generation
