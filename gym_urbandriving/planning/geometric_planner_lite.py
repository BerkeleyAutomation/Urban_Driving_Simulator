import numpy as np
import math
from gym_urbandriving.utils import Trajectory

class GeometricPlanner:
    """
    This class plans for all agents in a scene using bezier curves. Velocities behavior is undefined. 

    Parameters
    ----------
    optional_targets: list
        List of [x,y,a] optional targets to help guide planning. 
    """

    #TODO: remove other parameters when we end up ditching OMPL
    def __init__(self,state, inter_point_d=1.0, planning_time=1.0, optional_targets = None, num_cars = 0):
        if optional_targets is None:
            self.optional_targets_left = [[475,375,-np.pi/2],
                           [525,375,np.pi/2],
                           [625,475,-np.pi],
                           [625,525,0.0],
                           [475,625,-np.pi/2],
                           [525,625,np.pi/2],
                           [375,475,-np.pi],
                           [375,525,0.0]]
            self.optional_targets_right = [[440,375,-np.pi/2],
                           [560,375,np.pi/2],
                           [625,440,-np.pi],
                           [625,560,0.0],
                           [440,625,-np.pi/2],
                           [560,625,np.pi/2],
                           [375,440,-np.pi],
                           [375,560,0.0]]
            self.optional_targets_straight = [[450,375,-np.pi/2],
                           [550,375,np.pi/2],
                           [625,450,-np.pi],
                           [625,550,0.0],
                           [450,625,-np.pi/2],
                           [550,625,np.pi/2],
                           [375,450,-np.pi],
                           [375,550,0.0]]

    def plan(self,x0,y0,v0,a0,x1,y1,v1,a1):
        def interpolate(p0,p1,p2,p3,t):
            """
            Bezier curve interpolation using deCasteljau's algorithm
            """
            return [p0[0]*1.0*((1-t)**3) + p1[0]*3.0*t*(1-t)**2 + p2[0]*3.0*(t**2)*(1-t) + p3[0]*1.0*(t**3), p0[1]*1.0*((1-t)**3) + p1[1]*3.0*t*(1-t)**2 + p2[1]*3.0*(t**2)*(1-t) + p3[1]*1.0*(t**3)]

        distance_between_points = math.sqrt((x0-x1)**2+(y0-y1)**2)
        p0 = [x0,y0]
        p1 = [x0+.3*distance_between_points*np.cos(a0), y0 - .3*distance_between_points*np.sin(a0)]
        p2 = [x1-.3*distance_between_points*np.cos(a1), y1 + .3*distance_between_points*np.sin(a1)]
        p3 = [x1,y1]

        first_point = interpolate(p0,p1,p2,p3,0)
        res_path = [first_point]
        for t in np.arange(0,1,.001):
            new_point = interpolate(p0,p1,p2,p3,t)
            old_point = res_path[-1]
            if (new_point[0] - old_point[0])**2 + (new_point[1] - old_point[1])**2 > 1:
                res_path.append(new_point)

        num_points = len(res_path)
        for i in range(num_points):
            res_path[i].append(v0*(1-float(i)/float(num_points))+v1*(float(i)/float(num_points)))

        return res_path

    def plan_for_agents(self, state,type_of_agent='background_cars',agent_num=0):

        obj =  state.dynamic_objects[type_of_agent][str(agent_num)]
        if abs(((obj.destination[3]- obj.angle)+2*np.pi)%(2*np.pi)-(np.pi)/2)<np.pi/4:
            target1 = sorted(self.optional_targets_left, key=lambda p: (p[0]-obj.x)**2 + (p[1]-obj.y)**2)[0]
            target2 = sorted(self.optional_targets_left, key=lambda p: (p[0]-obj.destination[0])**2 + (p[1]-obj.destination[1])**2)[0]
        elif abs(((obj.destination[3]- obj.angle)+2*np.pi)%(2*np.pi)-(3*np.pi)/2)<np.pi/4:
            target1 = sorted(self.optional_targets_right, key=lambda p: (p[0]-obj.x)**2 + (p[1]-obj.y)**2)[0]
            target2 = sorted(self.optional_targets_right, key=lambda p: (p[0]-obj.destination[0])**2 + (p[1]-obj.destination[1])**2)[0]
        else:
            target1 = sorted(self.optional_targets_straight, key=lambda p: (p[0]-obj.x)**2 + (p[1]-obj.y)**2)[0]
            target2 = sorted(self.optional_targets_straight, key=lambda p: (p[0]-obj.destination[0])**2 + (p[1]-obj.destination[1])**2)[0]
 
        traj = Trajectory(mode = 'xyv')
        for p in self.plan(obj.x, obj.y, obj.vel, obj.angle, target1[0], target1[1], 1, target1[2]):
            traj.add_point(p)
        for p in self.plan(target1[0], target1[1], 1, target1[2], target2[0], target2[1], 1, target2[2]):
            traj.add_point(p)
        for p in self.plan(target2[0], target2[1], 1, target2[2], obj.destination[0], obj.destination[1], 1, obj.destination[3]):
            traj.add_point(p)

        obj.trajectory = traj

