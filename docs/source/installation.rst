Installation
============

Install FLUIDS
^^^^^^^^^^^^^^

::
   
   pip3 install gym-urbandriving

Install FLUIDS from Source
^^^^^^^^^^^^^^^^^^^^^^^^^^
These commands install gym-urbandriving and its requirements in the current Python environment. 
::
   
   git clone https://github.com/BerkeleyAutomation/Urban_Driving_Simulator.git
   cd Urban_Driving_Simulator
   pip3 install -e .


Optional OMPL Install
^^^^^^^^^^^^^^^^^^^^^

Additional trajectory generation features are available if OMPL (Open Motion Planning Library) is installed. The following is the installation instructino for Mac users.

Install Macports https://www.macports.org/install.php (Note macports is very heavily tied to xcode to guarantee this to work you will need to have xcode installed)
With macports installed perform the following three lines of code
::
	sudo port sync
	sudo port clean castxml
	sudo port install ompl +app

Macport will download its own version of python2.7 that everything will work off of. To link the command line python type the following:
::
	sudo port select python2 python2.7




