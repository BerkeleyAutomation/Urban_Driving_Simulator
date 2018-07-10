Installation
============

Installing FLUIDS Core
^^^^^^^^^^^^^^^^^^^^^^

The FLUIDS core simulator provides the core simulation environment. Currently only install from source is supported.

::

   git clone https://github.com/BerkeleyAutomation/Urban_Driving_Simulator.git
   cd Urban_Driving_Simulator
   pip3 install -e .

Installing FLUIDS Gym Environments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The FLUIDS Gym Environment is compatible with agents designed for OpenAI's Gym benchmark API. This interface layer depends on FLUIDS core.

::
   
   git submodule update --init --recursive
   pip3 install -e gym_fluids
