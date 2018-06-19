import numpy as np
from gym_urbandriving.actions import VelocityAction

class Trajectory(object):
    """
    General trajectory class. 

    Shape n x 7
        n is number of points
        7 dimensions: [x, y, velocity, angle, action steer, action angle, t]
    """

    def __init__(self, target='car', mode='xyvacst', fsm=0):
        """
        Initializes an empty general control. 

        Parameters
        ----------
        target : str
            any string containing 'xyvacst' in order. 
        """
        self._trajectory = np.zeros((0, 7))
        self.mode = mode

        self.dimensions_used = []
        for c in mode:
            if 'x' == c:
                self.dimensions_used.append(0)
            elif 'y' == c:
                self.dimensions_used.append(1)
            elif 'v' == c:
                self.dimensions_used.append(2)
            elif 'a' == c:
                self.dimensions_used.append(3)
            elif 'c' == c:
                self.dimensions_used.append(4)
            elif 's' == c:
                self.dimensions_used.append(5)
            elif 't' == c:
                self.dimensions_used.append(6)
            else:
                raise ValueError()
        self.fsm = fsm
        print("MADE NEW TRAJECTORY")
        self.stopped = True

    def get_matrix(self):
        """
        Returns underlying trajectory matrix. 

        Returns
        ----------
        self._trajectory : np array
        """        
        return self._trajectory

    def add_point(self, p):
        if p is None:
            return
        expanded_p = [p[self.dimensions_used.index(i)] if (i in self.dimensions_used) else np.nan for i in range(7)]
        self._trajectory = np.append(self._trajectory, [expanded_p], axis=0)

    def get_next_point(self, t):
        """
        Returns next point taking into account time.
        Specifically, returns the first point with time equal to or greater than specified time, or None if no points are left.  

        Returns
        ----------
        point : np array
        """   
        assert ('t' in self.mode)
        t_index = self.mode.index('t')
        res = self.first()
        while (res[t_index] < t and not self.is_empty()):
            self.pop()
            res = self.first()

        if self.is_empty():
            return None
        return res

    def get_point(self, index, t = None):
        return self._trajectory[index][self.dimensions_used]

    def get_renderable_points(self):
        return [[self._trajectory[i][self.mode.index('x')],self._trajectory[i][self.mode.index('y')]] for i in range(self.npoints())]

    def set_vel(self, target_vel):
        if target_vel == None:
            return
        v_index = self.mode.index('v')
        for i in range(self.npoints()):
            self._trajectory[i][v_index] = target_vel.get_value()

        if target_vel.get_value() == 0.0:
            self.stopped = True
        else:
            self.stopped = False

    def get_vel(self):
        v_index = self.mode.index('v')

        if self.is_empty():
            return VelocityAction(4.0)
        
        return VelocityAction(self._trajectory[-1][v_index])

    def get_points_list(self, start=0, end=None):
        if not end:
            end  = self.npoints()
        res = []
        for i in range(start, end):
            res.append(self._trajectory[i][self.dimensions_used].tolist())
        return np.array(res)

    def add_interpolated_t(self):
        self.mode += 't'
        self.dimensions_used.append(6)

        for t in range(self.npoints()):
            self._trajectory[t][6] = t

    def npoints(self):
        return self._trajectory.shape[0]

    def first(self):
        return self._trajectory[0][self.dimensions_used]

    def last(self):
        return self._trajectory[-1][self.dimensions_used]

    def pop(self):
        first = self.first()
        self._trajectory = self._trajectory[1:]
        return first

    def is_empty(self):
        return not self._trajectory.shape[0]
