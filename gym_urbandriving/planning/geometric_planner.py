from ompl import util as ou
from ompl import base as ob
from ompl import geometric as og
import numpy as np
from copy import deepcopy


class ValidityChecker(ob.StateValidityChecker):
    def __init__(self, si, state, controlled_obj):
        self.state = deepcopy(state)
        self.obj = controlled_obj
        self.state.dynamic_objects = [self.obj]
        #print(self.state.dynamic_objects)
        #print(self.state.static_objects)
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
        self.state.dynamic_objects = [self.obj]
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
    def __init__(self, state, inter_point_d=1.0, planning_time=1.0):
        self.state = deepcopy(state)
        self.state.dynamic_objects = []
        self.planning_time = planning_time
        self.inter_point_d = inter_point_d
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
            return None
        #print(sol.cost(pathObj).value())
        sol = sol.printAsMatrix()
        #print(sol)

        s = [[float(j) for j in i.split(" ")[:-1]] for i in sol.splitlines()][:-1]

        v0 = car.vel
        num_points = len(s)
        for i in range(num_points):
            [i].append(v0*(1-float(i)/float(num_points))+v1*(float(i)/float(num_points)))
        return s
