# FLUIDS: A First-Order Local Urban Intersection Driving Simulator

## Abstract

To facilitate automation of urban driving, we present an efficient, lightweight, open-source, first-order simulator with associated graphical display and algorithmic supervisors. The goal of FLUIDS is to allow for large-scale data collection of challenging simulated traffic intersections with varying state configurations and large-scale evaluation for early stage development of planning algorithms.  FLUIDS supports an image-based bird’s-eye state space and a lower dimensional quasi-LIDAR representation. FLUIDS additionally provides an implemented algorithmic planner as a baseline controller. We find that FLUIDS can gather data in parallel from the baseline controller at 4000 state-action pairs per minute and evaluate in parallel an imitation learned policy on the baseline at 20K evaluations per minute. We demonstrate the usefulness of FLUIDS' data collection speeds by training a velocity controller for avoiding collisions and obeying traffic laws using imitation learning on the provided baseline controller as the supervisor. We also use FLUIDS to automate an extensive sensitivity analysis of the learned model to various simulation parameters. FLUIDS 1.0 is available at https://github.com/BerkeleyAutomation/Urban_Driving_Simulator.

## Imitation Learning Supplementary Material

[Imitation Learning Supplementary Material](FLUIDS_IL.pdf)

## Demo Video ##
