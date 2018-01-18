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


# Dynamics model for our car. Ydim of car should be 40 (default)
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




class RRTMPlanner:
    def __init__(self, agents,planner=None,time=None, goal= None,prune = None,selection = None):
        self.agents = agents
        self.num_agents = len(agents)

        self.path = []
        self.planner = planner
        self.time = time
        self.goal = goal
        self.prune = prune
        self.selection = selection

    def propagate(self,start, control, duration, state):
    # Since the environment discretizes the actions, I set the planner to discretize by 1 timestep as well.

    
        assert(duration == 1.0)

        for i in range(self.num_agents):
            car_idx = i*4
            cntr_idx = i*2

            # Rest of these lines are from car kinematic step functions
            delta_f, a = control[cntr_idx], control[cntr_idx+1]
            delta_f = max(min(3, delta_f), -3)
            delta_f, rad_angle = np.radians(10*delta_f), np.radians(start[car_idx+3])

            vel = start[car_idx+2]
            if a > 5 - vel:
                a = 5 - vel
            elif a < -5 - vel:
                a = -5 - vel

            ode_state = [start[car_idx], start[car_idx+1], start[car_idx+2], rad_angle]
            aux_state = (a, delta_f)
            t = np.arange(0.0, 1.0, 0.1)
            delta_ode_state = odeint(integrator, ode_state, t, args=aux_state)
            x, y, vel, new_angle = delta_ode_state[-1]
            state[car_idx] = x
            state[car_idx+1] = y
            state[car_idx+2] = vel
            state[car_idx+3] = np.rad2deg(new_angle) % 360


    def plan(self, state):

        start_state = state
        # construct the state space we are planning in
        # State space will be [x, y, vel, angle]
        # Note: I found docs for ODEStateSpace and MorseStateSpace
        space = ob.RealVectorStateSpace(4*self.num_agents)
        
        
        # set the bounds for the R^2 part of SE(2)
        bounds = ob.RealVectorBounds(4*self.num_agents)
        
        for i in range(self.num_agents):
            car_idx = i*4
            bounds.setLow(car_idx, 0)
            bounds.setLow(car_idx+1, 0)
            bounds.setLow(car_idx+2, 0) # This is the velocity component. Set to a negative number to allow backtracking
            bounds.setLow(car_idx+3, 0)
            bounds.setHigh(car_idx+0, state.dimensions[0]) 
            bounds.setHigh(car_idx+1, state.dimensions[1])
            bounds.setHigh(car_idx+2, 5)
            bounds.setHigh(car_idx+3, 360)

        space.setBounds(bounds)

        # create a control space
        cspace = oc.RealVectorControlSpace(space, 2*self.num_agents)

        # set the bounds for the control space
        cbounds = ob.RealVectorBounds(2*self.num_agents)
        for i in range(self.num_agents):
            cbounds.setLow(-3.)
            cbounds.setHigh(3.)

        cspace.setBounds(cbounds)

        def isStateValid(spaceInformation, state):
            # perform collision checking or check if other constraints are
            # satisfied
            for i in range(self.num_agents):
                car_idx = i*4
                start_state.dynamic_objects[i].shapely_obj = None
                start_state.dynamic_objects[i].x = state[car_idx]
                start_state.dynamic_objects[i].y = state[car_idx+1]
                start_state.dynamic_objects[i].angle = state[car_idx+3]
                if start_state.collides_any(i):
                     return False
            return spaceInformation.satisfiesBounds(state)

        # define a simple setup class
        ss = oc.SimpleSetup(cspace)
        ss.setStateValidityChecker(ob.StateValidityCheckerFn(partial(isStateValid, ss.getSpaceInformation())))
        ss.setStatePropagator(oc.StatePropagatorFn(self.propagate))

        # create a start state
        start = ob.State(space)

        for i in range(self.num_agents):
            car_idx = i*4
            start()[car_idx] = state.dynamic_objects[i].x
            start()[car_idx+1] = state.dynamic_objects[i].y
            start()[car_idx+2] = state.dynamic_objects[i].vel
            start()[car_idx+3] = state.dynamic_objects[i].angle

        goal = ob.State(space);

        # create a goal state
        for i in range(self.num_agents):
            car_idx = i*4
            agent = self.agents[i]
            goal_state = agent.goal_state
        
            goal()[car_idx] = goal_state[0]
            goal()[car_idx+1] = goal_state[1]
            goal()[car_idx+2] = goal_state[2]
            goal()[car_idx+3] = goal_state[3]


        # set the start and goal states
        ss.setStartAndGoalStates(start, goal, 0.05)
        # (optionally) set planner
        si = ss.getSpaceInformation()


        if self.planner == 'RRT':
            planner = oc.RRT(si) # this is the default
        elif self.planner == 'SST':
            planner = oc.SST(si)
        elif self.planner == 'EST':
            planner = oc.EST(si)
        elif self.planner == 'KPIECE':
            planner = oc.KPIECE1(si)
        else:
            planner = oc.RRT(si)

        planner.setSelectionRadius(self.selection)
        planner.setPruningRadius(self.prune)
        
        planner.setGoalBias(self.goal)
        ss.setPlanner(planner)
        # (optionally) set propagation step size
        si.setPropagationStepSize(1) # Propagation step size should be 1 to match our model
        
        # attempt to solve the problem
        if not self.time == None:
            solved = ss.solve(self.time) # 30 second time limit
        else: 
            solved = ss.solve(30.0)

       

        if solved:
            # print the path to screen
            print("Found solution:\n%s" % ss.getSolutionPath())
            path = ss.getSolutionPath().printAsMatrix()
            path = [l.split(" ") for l in path.splitlines()]

            num_controls = 2*self.num_agents+1
            
            path = [[float(i) for i in l][-num_controls:] for l in path][1:]
            paths = []
            for i in range(self.num_agents):
                car_idx = i*2
                agent_path = []
                for control in path:
                    for r in range(int(control[-1])):
                        agent_path.append((control[car_idx],control[car_idx+1]))
                
                paths.append(agent_path)

            return paths
        else:
            return None
        
        

        
            
