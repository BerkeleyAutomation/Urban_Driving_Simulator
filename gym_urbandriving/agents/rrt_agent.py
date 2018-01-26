import numpy as np
from functools import partial
from ompl import util as ou
from ompl import base as ob
from ompl import control as oc
from ompl import geometric as og
from scipy.integrate import odeint
import IPython

# Only SyclopsRRT and SyclopsEST use this, and both those planners fail in a highly constrained environment
# I suspect its because of the sampleUniform. When planning, I observe that those 2 planners explore many invalid states
class MyDecomposition(oc.GridDecomposition):
    def __init__(self, length, bounds):
        super(MyDecomposition, self).__init__(length, 2, bounds)
    def project(self, s, coord):
        coord[0] = s[0]
        coord[1] = s[1]
    def sampleFullState(self, sampler, coord, s):
        sampler.sampleUniform(s)
        s[0] = coord[0]
        s[1] = coord[1]

class RRTAgent:
    def __init__(self, agent_num=0):
        self.agent_num = agent_num
        self.path = []

    def eval_policy(self, state):

        if len(self.path):
            # If we have a stored path just evaluate those steps

            return self.path.pop(0)
            
        start_state = state
        # construct the state space we are planning in
        # State space will be [x, y, vel, angle]
        # Note: I found docs for ODEStateSpace and MorseStateSpace
        space = ob.RealVectorStateSpace(4)
        
        
        # set the bounds for the R^2 part of SE(2)
        bounds = ob.RealVectorBounds(4)
        bounds.setLow(0, 0)
        bounds.setLow(1, 0)
        bounds.setLow(2, -5) # This is the velocity component. Set to a negative number to allow backtracking
        bounds.setLow(3, 0)
        bounds.setHigh(0, state.dimensions[0]) 
        bounds.setHigh(1, state.dimensions[1])
        bounds.setHigh(2, 5)
        bounds.setHigh(3, 360)
        space.setBounds(bounds)
        # create a control space
        cspace = oc.RealVectorControlSpace(space, 2)

        # set the bounds for the control space
        cbounds = ob.RealVectorBounds(2)
        cbounds.setLow(-3.)
        cbounds.setHigh(3.)
        cspace.setBounds(cbounds)

        def isStateValid(spaceInformation, state):
            # perform collision checking or check if other constraints are
            # satisfied
            start_state.dynamic_objects[self.agent_num].shapely_obj = None
            start_state.dynamic_objects[self.agent_num].x = state[0]
            start_state.dynamic_objects[self.agent_num].y = state[1]
            start_state.dynamic_objects[self.agent_num].angle = state[3]
            return spaceInformation.satisfiesBounds(state) and not start_state.collides_any(self.agent_num)

        def propagate(start, control, duration, state):
            # Since the environment discretizes the actions, I set the planner to discretize by 1 timestep as well.
            assert(duration == 1.0)

            action = (control[0], control[1])

            obj = start_state.dynamic_objects[self.agent_num]
            if obj.dynamics_model == "kinematic":
                state[0], state[1], state[2], state[3] = obj.kinematic_model_step(action, start[0], start[1], start[2], start[3])
            else:
                state[0], state[1], state[2], state[3] = obj.point_model_step(action, start[0], start[1], start[2], start[3])


        # define a simple setup class
        ss = oc.SimpleSetup(cspace)
        ss.setStateValidityChecker(ob.StateValidityCheckerFn(partial(isStateValid, ss.getSpaceInformation())))
        ss.setStatePropagator(oc.StatePropagatorFn(propagate))

        # create a start state
        start = ob.State(space)
        start()[0] = state.dynamic_objects[self.agent_num].x
        start()[1] = state.dynamic_objects[self.agent_num].y
        start()[2] = state.dynamic_objects[self.agent_num].vel
        start()[3] = state.dynamic_objects[self.agent_num].angle

        # create a goal state
        goal = ob.State(space);
        goal()[0] = 450
        goal()[1] = 900
        goal()[2] = 2
        goal()[3] = 270

        # set the start and goal states
        ss.setStartAndGoalStates(start, goal, 0.05)
        # (optionally) set planner
        si = ss.getSpaceInformation()
        planner = oc.RRT(si)
        #planner = oc.EST(si)
        #planner = oc.KPIECE1(si) # this is the default
        # SyclopEST and SyclopRRT require a decomposition to guide the search
        #decomp = MyDecomposition(500, bounds)
        #planner = oc.SyclopEST(si, decomp)
        #planner = oc.SyclopRRT(si, decomp)
        ss.setPlanner(planner)
        # (optionally) set propagation step size
        si.setPropagationStepSize(1) # Propagation step size should be 1 to match our model
        
        # attempt to solve the problem
        solved = ss.solve(30.0) # 30 second time limit

        if solved:
            # print the path to screen
            print("Found solution:\n%s" % ss.getSolutionPath())
            path = ss.getSolutionPath().printAsMatrix()
            path = [l.split(" ") for l in path.splitlines()]
            path = [[float(i) for i in l][-3:] for l in path][1:]
            for a, b, s in path:
                for i in range(int(s)):
                    self.path.append((a, b))
        

        if len(self.path):
            return self.path.pop(0)

        return
            
