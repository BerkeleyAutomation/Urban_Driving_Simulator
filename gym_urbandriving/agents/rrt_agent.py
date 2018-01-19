import numpy as np
from functools import partial
from ompl import util as ou
from ompl import base as ob
from ompl import control as oc
from ompl import geometric as og
from scipy.integrate import odeint

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
        self.target_y = None

    def eval_policy(self, state):

        if len(self.path):
            # If we have a stored path just evaluate those steps
            return self.path.pop(0)
            
        if self.target_y is None:
            self.target_y = list(range((int)(state.dynamic_objects[self.agent_num].y),900,10))
            print self.target_y

        start_state = state
        current_state = [state.dynamic_objects[self.agent_num].x, 
                         state.dynamic_objects[self.agent_num].y, 
                         state.dynamic_objects[self.agent_num].vel, 
                         state.dynamic_objects[self.agent_num].angle]

        for index in range(len(self.target_y)-1):

            # construct the state space we are planning in
            # State space will be [x, y, vel, angle]
            # Note: I found docs for ODEStateSpace and MorseStateSpace
            space = ob.RealVectorStateSpace(4)
            
            
            # set the bounds for the R^2 part of SE(2)
            bounds = ob.RealVectorBounds(4)
            min_x, max_x, min_y, max_y = current_state[0]-50, current_state[0]+50, min(current_state[1], self.target_y[index+1])-50, max(current_state[1], self.target_y[index+1])+50
            bounds.setLow(0, min_x)
            bounds.setLow(1, min_y)
            bounds.setLow(2, -5) # This is the velocity component. Set to a negative number to allow backtracking
            bounds.setLow(3, 0)
            bounds.setHigh(0, max_x) 
            bounds.setHigh(1, max_y)
            bounds.setHigh(2, 5)
            bounds.setHigh(3, 360)
            space.setBounds(bounds)
            # create a control space
            cspace = oc.RealVectorControlSpace(space, 2)

            # set the bounds for the control space
            cbounds = ob.RealVectorBounds(2)
            cbounds.setLow(0,-3)
            cbounds.setHigh(0,3.)
            cbounds.setLow(1,-1.)
            cbounds.setHigh(1,3.)
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
            start()[0] = current_state[0]
            start()[1] = current_state[1]
            start()[2] = current_state[2]
            start()[3] = current_state[3]

            # create a goal state
            goal = ob.State(space);
            goal()[0] = 450
            goal()[1] = self.target_y[index+1]
            goal()[2] = 4
            goal()[3] = 270

            # set the start and goal states
            ss.setStartAndGoalStates(start, goal, 0.05)
            # (optionally) set planner
            si = ss.getSpaceInformation()
            planner = oc.SST(si)

            planner.setGoalBias(.0)
            #planner.setPruningRadius(.05)
            #planner.setSelectionRadius(10)

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
            solved = ss.solve(.1) # 30 second time limit

            if solved:
                # print the path to screen
                print("Found solution:\n%s" % ss.getSolutionPath())
                path_matrix = ss.getSolutionPath().printAsMatrix()
                path_string = [l.split(" ") for l in path_matrix.splitlines()]
                path_list = [[float(i) for i in l][-3:] for l in path_string][1:]
                for a, b, s in path_list:
                    for i in range(int(s)):
                        self.path.append((a, b))

                current_state = [[float(i) for i in l][:4] for l in path_string][-1]

        if len(self.path):
            return self.path.pop(0)

        return
            
