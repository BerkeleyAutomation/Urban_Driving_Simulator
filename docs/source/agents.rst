Agents
======

Background 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 Used internally to control agents in the scene such as traffic lights, cross walks, pedestrians and background cars. These are not intended to be instantiated outside the UDS environment

.. autoclass:: gym_urbandriving.agents.background.planning_pursuit_agent.PlanningPursuitAgent
   :members: eval_policy
.. autoclass:: gym_urbandriving.agents.background.pursuit_agent.PursuitAgent
   :members: eval_policy

Hierarchical
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Used to build control at different levels of the planning software stack. They are used internally in FLUIDS to allow the user to apply a different type of actions to the environment. 

.. autoclass:: gym_urbandriving.agents.hierarchical.velocity_action_agent.VelocityActionAgent
   :members: eval_policy
.. autoclass:: gym_urbandriving.agents.hierarchical.steering_action_agent.SteeringActionAgent
   :members: eval_policy

Supervisors
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Classes use to control different cars in the scene. Logically they are similar to background cars and have access to the internal state of the world to make a decision. However, they can be used to collect data and provide ground truth of what the supervisor would have done in a single state. 

.. autoclass:: gym_urbandriving.agents.supervisor.velocity_supervisor.VelocitySupervisor
   :members: eval_policy
.. autoclass:: gym_urbandriving.agents.supervisor.steering_supervisor.SteeringSupervisor
   :members: eval_policy

Tele-Op
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Used for a human supervisor to operate the vehicle. Currently, the use of keyboard commands is supported. 

.. autoclass:: gym_urbandriving.agents.tele_op.keyboard_agent.KeyboardAgent
   :members: eval_policy
