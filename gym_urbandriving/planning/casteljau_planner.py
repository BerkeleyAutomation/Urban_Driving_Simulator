import numpy as np
import math

class CasteljauPlanner:
    def __init__(self):
        pass

    def plan(self,x0,y0,v0,a0,x1,y1,v1,a1):
        def interpolate(p0,p1,p2,p3,t):
            return [p0[0]*1.0*((1-t)**3) + p1[0]*3.0*t*(1-t)**2 + p2[0]*3.0*(t**2)*(1-t) + p3[0]*1.0*(t**3), p0[1]*1.0*((1-t)**3) + p1[1]*3.0*t*(1-t)**2 + p2[1]*3.0*(t**2)*(1-t) + p3[1]*1.0*(t**3)]

        distance_between_points = math.sqrt((x0-x1)**2+(y0-y1)**2)
        p0 = [x0,y0]
        p1 = [x0+.5*distance_between_points*np.cos(a0), y0 - .5*distance_between_points*np.sin(a0)]
        p2 = [x1-.5*distance_between_points*np.cos(a1), y1 + .5*distance_between_points*np.sin(a1)]
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