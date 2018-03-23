# FLUIDS: A First-Order Local Urban Intersection Driving Simulator

## Abstract

To facilitate automation of urban driving, we present an efficient, lightweight, open-source, first-order simulator with associated graphical display and algorithmic supervisors. The goal of FLUIDS is to allow for large-scale data collection of challenging simulated traffic intersections with varying state configurations and large-scale evaluation for early stage development of planning algorithms.  FLUIDS supports an image-based bird’s-eye state space and a lower dimensional quasi-LIDAR representation. FLUIDS additionally provides an implemented algorithmic planner as a baseline controller. We find that FLUIDS can gather data in parallel from the baseline controller at 4000 state-action pairs per minute and evaluate in parallel an imitation learned policy on the baseline at 20K evaluations per minute. We demonstrate the usefulness of FLUIDS' data collection speeds by training a velocity controller for avoiding collisions and obeying traffic laws using imitation learning on the provided baseline controller as the supervisor. We also use FLUIDS to automate an extensive sensitivity analysis of the learned model to various simulation parameters. FLUIDS 1.0 is available at https://github.com/BerkeleyAutomation/Urban_Driving_Simulator.

## Benchmarking FLUIDS With Imitation Learning
We evaluate the effectiveness of FLUIDS for learning policies by applying Imitation Learning to learn components of its planning stack. We study how quickly FLUIDS can collect data and how fast FLUIDS can evaluate the learned policy's performance and sensitivity to noise.

In IL, a supervisor provides demonstrations to an agent, and a policy mapping observed states to controls is learned. Imitation learning has been applied for on robots for tasks of grasping in clutter<sup>1</sup> and two-hand grasping<sup>2</sup>. For our purposes, the states are the LIDAR view and the controls will be the target velocity. We chose to learn this part of the pipeline because it is the most computationally expensive for the implemented supervisor. 

We can formalize this learning as follows: denote a policy as a measurable function $\pi: \mathcal{X} \to \mathcal{V}$ from the driver's view state space $\mX$ to target velocities inputs $\mathcal{V}$. We consider policies $\pi_{\theta}:\mathcal{X}\to \mathcal{U}$ parameterized by some $\theta\in \Theta$, such as the weights of a neural network.

Under the assumptions, any such policy $\pi_{\theta}$ induces a probability density over the set of trajectories of length $T$: $$p(\tau | \pi_\theta)=
p(\bx_0)\prod_{t=0}^{T-1} p(\bx_{t+1}|\pi_{\theta}(\bx_t),\bx_t)\,,$$
where a trajectory $\tau$ of length $T$ is a sequence of state and velocity tuples: $\tau = \{(\bx_t, v_t)\}_{t=0}^{T-1}$


We collect demonstrations using FLUIDS' velocity planner  $\pi_{\theta^*}$, where $\theta^*$ may not be contained in $\Theta$. We randomize the parameters of the simulation for each rollout, randomly adjusting the number of cars and positions using the simulator's model. The number of cars is uniform random between 2 and 8. To reduce the effect of errors compounding from execution, we also inject noise in the supervisor's velocity controller when generating training data~\cite{laskey2017dart}.

We measure the difference between the two learners and supervisor using a surrogate loss $l : \mathcal{V} \times \mathcal{V} \rightarrow \mathbb{R}$ <sup>~\cite{ross2011reduction,ross2010efficient}.
The surrogate loss we consider is the indicator function, since the target velocities are discretized, $l(v_1,v_2) = \mathbb{1}(v_1 \neq v_2) $. The objective of LfD is to minimize the expected surrogate loss under the distribution induced by the robot's policy:

\begin{equation}\label{eq:main_obj}
\underset{\theta}{\mbox{min }} E_{p(\tau|\pi_\theta)} \sum^{T-1}_{t=0}l(\pi_{\theta}(\bx_t), \pi_{\theta^*}(\bx_t))\,.
\end{equation}

However, in practice, this objective is difficult to optimize because of the coupling between the loss and the robot's distribution on states. Thus, we instead minimize an upper-bound on this objective~\cite{laskey2017comparing} via sampling $N$ trajectories from the supervisor's policy. 

\begin{equation}\label{eq:main_obj}
\underset{\theta}{\mbox{min }} \sum^{N-1}_{n=0} \sum^{T-1}_{t=0}l(\pi_{\theta}(\bx_{t,n}), \pi_{\theta^*}(\bx_{t,n}))\,; \quad \tau \sim p(\tau|\pi_{\theta^*})\,.
\end{equation}

Our learner is the decision tree implemented in SciKit-Learn. We pose the problem as a classification task for the learner to identify the correct velocity control (accelerate or stop) given the state observation. We featurize the state using the quasi-LIDAR featurization offered by FLUIDS. 


<sup>1</sup>Laskey, Michael, et al. "Robot grasping in clutter: Using a hierarchy of supervisors for learning from demonstrations." Automation Science and Engineering (CASE), 2016 IEEE International Conference on. IEEE, 2016.

<sup>2</sup>Zhang, Tianhao, et al. "Deep Imitation Learning for Complex Manipulation Tasks from Virtual Reality Teleoperation." arXiv preprint arXiv:1710.04615 (2017).
