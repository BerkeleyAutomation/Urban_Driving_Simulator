import numpy as np
from functools import partial
from ompl import util as ou
from ompl import base as ob
from ompl import control as oc
from ompl import geometric as og
from scipy.integrate import odeint

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
        #s.setXY(coord[0], coord[1])
## @endcond



def integrator(state, t, acc, delta_f):
    x, y, vel, rad_angle = state

    # Differential equations
    beta = np.arctan((20. / (20. + 20.)) * np.tan(delta_f))
    dx = vel * np.cos(rad_angle + beta)
    dy = vel * -np.sin(rad_angle + beta)
    dangle = (vel / 20.) * np.sin(beta)
    dvel = acc
    output = [dx, dy, dvel, dangle]
    return output


def propagate(start, control, duration, state):
    assert(duration == 1.0)
    delta_f, a = control[0], control[1]
    rad_angle = np.radians(start[3])
    delta_f = np.radians(10*delta_f)

    vel = start[2]
    if a > 5 - vel:
        a = 5 - vel
    elif a < -5 - vel:
        a = -5 - vel

    ode_state = [start[0], start[1], start[2], rad_angle]
    aux_state = (a, delta_f)
    t = np.arange(0.0, 1.0, 0.1)
    delta_ode_state = odeint(integrator, ode_state, t, args=aux_state)
    x, y, vel, new_angle = delta_ode_state[-1]
    state[0] = x
    state[1] = y
    state[2] = vel
    state[3] = np.rad2deg(new_angle) % 360

class RRTAgent:
    def __init__(self, agent_num=0):
        self.agent_num = agent_num
        self.path = []

    def eval_policy(self, state):
        if len(self.path):
            return self.path.pop(0)
        start_state = state
        # construct the state space we are planning in
        space = ob.RealVectorStateSpace(4)
        # set the bounds for the R^2 part of SE(2)
        bounds = ob.RealVectorBounds(4)
        bounds.setLow(0, 0)
        bounds.setLow(1, 0)
        bounds.setLow(2, -5)
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
            print(spaceInformation, state)
            return spaceInformation.satisfiesBounds(state)

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
        goal()[0] = 500
        goal()[1] = 500
        goal()[2] = 0
        goal()[3] = 0

        # set the start and goal states
        ss.setStartAndGoalStates(start, goal, 0.05)
        # (optionally) set planner
        si = ss.getSpaceInformation()
        #planner = oc.RRT(si)
        #planner = oc.EST(si)
        #planner = oc.KPIECE1(si) # this is the default
        # SyclopEST and SyclopRRT require a decomposition to guide the search
        decomp = MyDecomposition(32, bounds)
        planner = oc.SyclopEST(si, decomp)
        #planner = oc.SyclopRRT(si, decomp)
        ss.setPlanner(planner)
        # (optionally) set propagation step size
        si.setPropagationStepSize(1)
        
        # attempt to solve the problem
        solved = ss.solve(10.0)

        if solved:
            # print the path to screen
            print("Found solution:\n%s" % ss.getSolutionPath())
            path = ss.getSolutionPath().printAsMatrix()
            path = [l.split(" ") for l in path.splitlines()]
            path = [[float(i) for i in l][-3:] for l in path][1:]
            #path = np.array(path)
            print(path)
            for a, b, s in path:
                for i in range(int(s)):
                    self.path.append((a, b))
            
        print(self.path)
        return self.path.pop(0)
