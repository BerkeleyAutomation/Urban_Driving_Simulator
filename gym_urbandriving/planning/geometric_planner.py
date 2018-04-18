from ompl import util as ou
from ompl import base as ob
from ompl import geometric as og
import numpy as np
from copy import deepcopy
from gym_urbandriving.utils import Trajectory

import scipy as sc
import scipy.interpolate
from scipy.interpolate import UnivariateSpline
from skimage import transform
from gym_urbandriving.actions import VelocityAction


class ValidityChecker(ob.StateValidityChecker):
    def __init__(self, si, state, controlled_obj):
        self.state = deepcopy(state)
        self.obj = controlled_obj
        self.state.dynamic_objects = {'background_cars':{}}
        self.state.dynamic_objects['background_cars']['0']=self.obj
       
        super(ValidityChecker, self).__init__(si)
    def isValid(self, s):
        x = s[0]
        y = s[1]
        angle = s[2]
        self.obj.set_pos(x, y, 0, angle)
        return not self.state.collides_any(0)


class MotionValidityChecker(ob.MotionValidator):
    def __init__(self, si, state, controlled_obj):
        self.state = deepcopy(state)
        self.obj = controlled_obj


        self.state.dynamic_objects = {'background_cars':{}}
        self.state.dynamic_objects['background_cars']['0']=self.obj
        super(MotionValidityChecker, self).__init__(si)
    def isValid(self, s):
        x = s[0]
        y = s[1]
        angle = s[2]
        self.obj.set_pos(x, y, 0, angle)
        return not self.state.collides_any(0)
    def checkMotion(self, s1, s2):
        if not self.isValid(s2):
            return False
        x, y, a = s1[0], s1[1], s1[2]
        xt, yt, at = s2[0], s2[1], s2[2]
        yd, xd = yt - y, xt - x
        ax = np.arctan(yd / (xd + 0.0001))
        ax = ax % (np.pi)
        ad = min(np.abs(at - ax), np.abs((ax - at)))
        return float(ad) < float(np.pi/4)

class GeometricPlanner:
    def __init__(self, state, inter_point_d=1.0, planning_time=1.0, optional_targets = None, num_cars = 0):
        self.state = deepcopy(state)
        self.state.dynamic_objects = []
        self.planning_time = planning_time
        self.inter_point_d = inter_point_d
        self.optional_targets = [[450,375,-np.pi/2],
                       [550,375,np.pi/2],
                       [625,450,-np.pi],
                       [625,550,0.0],
                       [450,625,-np.pi/2],
                       [550,625,np.pi/2],
                       [375,450,-np.pi],
                       [375,550,0.0]]

        self.num_cars = num_cars

    def plan_all_agents(self, state):
        for obj in state.dynamic_objects[:self.num_cars]:
            orig_obj = obj
            obj = deepcopy(obj)
            obj.vel = 4
            closest_point = sorted(self.optional_targets, key = lambda p: (p[0]-obj.x)**2+(p[1]-obj.y)**2 )[0]
            mid_target = sorted(self.optional_targets, key = lambda p: (p[0]-obj.destination[0])**2+(p[1]-obj.destination[1])**2)[0]
            traj = Trajectory(mode = 'xyv', fsm=0)

            path_to_follow = self.plan(obj, closest_point[0], closest_point[1], 4, closest_point[2])
            for p in path_to_follow:
                traj.add_point(p)
            #print(closest_point)
            obj.set_pos(closest_point[0], closest_point[1], 4, closest_point[2])
            path_to_follow = self.plan(obj, mid_target[0],mid_target[1],4,mid_target[2])
            for p in path_to_follow:
                traj.add_point(p)
                
            obj.set_pos(mid_target[0], mid_target[1], 4, mid_target[2])
            path_to_follow = self.plan(obj, obj.destination[0], obj.destination[1], 4, obj.destination[3])
            for p in path_to_follow:
                traj.add_point(p)

            orig_obj.trajectory = traj
            orig_obj.vel = 0
            orig_obj.trajectory.set_vel(4)
            
            #print(orig_obj.trajectory.get_points_list())
            npoints = orig_obj.trajectory.npoints()
            points = orig_obj.trajectory.get_points_list()
            xp, yp = points[:,0], points[:,1]

            splx = np.poly1d(np.polyfit(np.arange(npoints), xp, deg=4))
            sply = np.poly1d(np.polyfit(np.arange(npoints), yp, deg=4))
            splx = sc.interpolate.interp1d(np.arange(npoints), xp, 'cubic')
            sply = sc.interpolate.interp1d(np.arange(npoints), yp, 'cubic')
            #splx = UnivariateSpline(np.arange(npoints), points[:,0])
            #sply = UnivariateSpline(np.arange(npoints), points[:,1])
            #splx.set_smoothing_factor(0.9)
            #sply.set_smoothing_factor(0.9)


            xn = splx(np.linspace(0,npoints-1,200))
            yn = sply(np.linspace(0,npoints-1,200))
            xn = sc.ndimage.filters.gaussian_filter1d(xn, 15)
            yn = sc.ndimage.filters.gaussian_filter1d(yn, 15)

            #sc.interpolate.splprep([newx, newy], s=0)
            newtraj = Trajectory(mode = 'xyv', fsm=0)
            for x, y in zip(xn, yn):
                newtraj.add_point((x, y, 4))
            newtraj.set_vel(4)
            orig_obj.trajectory = newtraj

    def plan_for_agents(self, state,type_of_agent='background_cars',agent_num=0):

            obj =  state.dynamic_objects[type_of_agent][str(agent_num)]
            orig_obj = obj
            obj = deepcopy(obj)
            obj.vel = 4
            closest_point = sorted(self.optional_targets, key = lambda p: (p[0]-obj.x)**2+(p[1]-obj.y)**2 )[0]
            mid_target = sorted(self.optional_targets, key = lambda p: (p[0]-obj.destination[0])**2+(p[1]-obj.destination[1])**2)[0]
            traj = Trajectory(mode = 'xyv', fsm=0)

            path_to_follow = self.plan(obj, closest_point[0], closest_point[1], 4, closest_point[2])
            for p in path_to_follow:
                traj.add_point(p)
            #print(closest_point)
            obj.set_pos(closest_point[0], closest_point[1], 4, closest_point[2])
            path_to_follow = self.plan(obj, mid_target[0],mid_target[1],4,mid_target[2])
            for p in path_to_follow:
                traj.add_point(p)
                
            obj.set_pos(mid_target[0], mid_target[1], 4, mid_target[2])
            path_to_follow = self.plan(obj, obj.destination[0], obj.destination[1], 4, obj.destination[3])
            for p in path_to_follow:
                traj.add_point(p)

            orig_obj.trajectory = traj
            orig_obj.vel = 0
            orig_obj.trajectory.set_vel(VelocityAction(4))
            
            
            npoints = orig_obj.trajectory.npoints()
            points = orig_obj.trajectory.get_points_list()
            xp, yp = points[:,0], points[:,1]

            splx = np.poly1d(np.polyfit(np.arange(npoints), xp, deg=4))
            sply = np.poly1d(np.polyfit(np.arange(npoints), yp, deg=4))
            splx = sc.interpolate.interp1d(np.arange(npoints), xp, 'cubic')
            sply = sc.interpolate.interp1d(np.arange(npoints), yp, 'cubic')

            xn = splx(np.linspace(0,npoints-1,200))
            yn = sply(np.linspace(0,npoints-1,200))
            xn = sc.ndimage.filters.gaussian_filter1d(xn, 15)
            yn = sc.ndimage.filters.gaussian_filter1d(yn, 15)

            #sc.interpolate.splprep([newx, newy], s=0)
            newtraj = Trajectory(mode = 'xyv', fsm=0)
            for x, y in zip(xn, yn):
                newtraj.add_point((x, y, 4))
            newtraj.set_vel(VelocityAction(4))
            orig_obj.trajectory = newtraj

    def plan(self, controlled_object, x1, y1, v1, a1):
        a1 = (a1 + 2*np.pi) % (2 * np.pi)

        car = deepcopy(controlled_object)

        space = ob.RealVectorStateSpace(3)
        bounds = ob.RealVectorBounds(3)
        bounds.setLow(0, 0)
        bounds.setLow(1, 0)
        bounds.setLow(2, 0)
        bounds.setHigh(0, 1000)
        bounds.setHigh(1, 1000)
        bounds.setHigh(2, 2*np.pi)
        space.setBounds(bounds)
        si = ob.SpaceInformation(space)

        validityChecker = ValidityChecker(si, self.state, car)
        si.setStateValidityChecker(validityChecker)
        #si.setMotionValidator(MotionValidityChecker(si, state, agent_num))
        si.setup()

        start = ob.State(space)
        start[0] = car.x
        start[1] = car.y
        start[2] = car.angle

        goal = ob.State(space)
        goal[0] = x1
        goal[1] = y1
        goal[2] = a1

        pdef = ob.ProblemDefinition(si)
        pdef.setStartAndGoalStates(start, goal)
        pdef.setOptimizationObjective(ob.PathLengthOptimizationObjective(si))
        def objStateCost(state):
            return ob.Cost(0)

        def objMotionCost(state1, state2):
            x, y, a = state1[0], state1[1], state1[2]
            xt, yt, at = state2[0], state2[1], state2[2]
            yd, xd = yt - y, xt - x
            ax = np.arctan(yd / (xd + 0.001))
            ax = ax % (np.pi)
            if yd < 0:
                ax = ax + np.pi
            ad = min(np.abs(at - ax), np.abs((ax - at)))
            return 10*ad

        pathObj = ob.OptimizationObjective(si)
        pathObj.stateCost = objStateCost
        pathObj.motionCost = objMotionCost
        pathObj.setCostThreshold(1)

    #pdef.setOptimizationObjective(pathObj)

        optimizingPlanner = og.RRTstar(si)
        optimizingPlanner.setRange(self.inter_point_d)
        optimizingPlanner.setProblemDefinition(pdef)
        optimizingPlanner.setup()

        solved = optimizingPlanner.solve(self.planning_time)
        sol = pdef.getSolutionPath()

        if not sol:
            return []
        
        sol = sol.printAsMatrix()
       

        s = [[float(j) for j in i.split(" ")[:-1]] for i in sol.splitlines()][:-1]

        v0 = car.vel
        num_points = len(s)
        for i in range(num_points):
            [i].append(v0*(1-float(i)/float(num_points))+v1*(float(i)/float(num_points)))
        return s
