Installation
============

Installing FLUIDS Core
^^^^^^^^^^^^^^^^^^^^^^

The FLUIDS core simulator provides the core simulation environment. Currently only install from source is supported.

::

   git clone https://github.com/BerkeleyAutomation/Urban_Driving_Simulator.git
   cd Urban_Driving_Simulator
   git checkout v2
   pip3 install -e .

Installing FLUIDS Gym Environments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The FLUIDS Gym Environment is compatible with agents designed for OpenAI's Gym benchmark API. This interface layer depends on FLUIDS core.

::
   
   git clone https://github.com/BerkeleyAutomation/gym_fluids.git
   cd gym_fluids
   pip3 install -e .
