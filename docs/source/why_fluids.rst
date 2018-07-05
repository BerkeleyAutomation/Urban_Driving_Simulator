Why FLUIDS?
=============
To study and compare Reinforcement and Imitation Learning algorithms, the most commonly used benchmarks are OpenAI Gym, Mujoco, and ATARI games. However, these benchmarks generally fail to capture real-life challenges to learning algorithms, including multi-agent interactions, noisy sensors, and generalization. FLUIDS aims to fill this gap by providing a fast, birds-eye simulation of cars and pedestrians in an urban driving setting. Below, we highlight several notable capabilities of FLUIDS.

Tests Generalization
^^^^^^^^^^^^^^^^^^^^^^^
FLUIDS is designed to test how well agents generalize to new environments that are both in and out of sample from the initial state distribution. The initial state distribution can be specified to be a range of cars on the road starting at various lane positions. The randomness stems from the number of cars currently on the road and the location of each car. 

To test how robust a policy is to out of sample distributions, FLUIDS allows for perturbations such as enabling pedestrians, varying traffic light timing and changing the amount of noise in the sensor readings.


Multi-Agent Planning
^^^^^^^^^^^^^^^^^^^^^
Another advantage of FLUIDS is that the number of supervisors that can be controlled by an agent and that controlled by the simulator is variable. Experiments such as coordinating a fleet of self-driving cars traversing an intersection or having a single self-driving car pass an intersection with multiple cars and pedestrians are all supported.

Built-in Supervisors
^^^^^^^^^^^^^^^^^^^^^
In order to collect consist training data for Imitation Learning experiments and a baseline for performance. FLUIDS provides access to an array of supervisors, which can perform the driving tasks by having access to the global state of the world. The algorithms for the supervisors are the same planning stack used for the background agents. 
