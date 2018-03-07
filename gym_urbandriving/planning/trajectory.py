import numpy as np
from skimage import transform

# Four corners of the interection, hard-coded in camera space
corners = np.array([[765, 385],
                    [483, 470],
                    [1135, 565],
                    [1195, 425]])

# Four corners of the intersection, hard-coded in transformed space
st_corners = np.array([[400, 400],
                       [400, 600],
                       [600, 600],
                       [600, 400]])
tf_mat = transform.ProjectiveTransform()
tf_mat.estimate(st_corners, corners)

def transform_point(x, y, w=1280, h=720):
    x, y = x * w, y * h
    tx, ty = tf_mat.inverse(np.array((x,y)))[0]
    tx *= 1.04
    ty *= 1.17
    return tx, ty

def from_table(traj_table):
    # Returns a list containing every unlabeld point, and a list of labeled trajectories
    unlabeled_trajectory = []
    traj_holder = {}
    for t, frame in enumerate(trajectories):
        for x, y, cls, label in frame:
            if label >= 0:
                if label in traj_holder:
                    traj_holder[label].add_camera_point(x, y, t)
                else:
                    traj_holder[label] = Trajectory(target={7:'ped',15:'car'}[cls])
                    traj_holder[label].add_camera_point(x, y, t)
            else:
                unlabeled_trajectory.append((x, y, cls, t))
    return unlabeled_trajectory, traj_holder
                
    

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
            <?>
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
        if 't' in self.mode:
            t_index = self.mode.index('t')
            t = p[t_index]
            if t < 0 and self.is_empty():
                t = 0
            elif t < 0:
                t = self._trajectory[-1][t_index] + 1

        expanded_p = [p[self.dimensions_used.index(i)] if (i in self.dimensions_used) else np.nan for i in range(7)]
        self._trajectory = np.append(self._trajectory, [expanded_p], axis=0)

    def get_point(self, index):
        return self._trajectory[index][self.dimensions_used]

    def get_renderable_points(self):
        return [[self._trajectory[i][self.mode.index('x')],self._trajectory[i][self.mode.index('y')]] for i in range(self.npoints())]

    def set_vel(self, target_vel):
        if target_vel == None:
            return
        v_index = self.mode.index('v')
        for i in range(self.npoints()):
            self._trajectory[i][v_index] = target_vel
        if target_vel == 0:
            self.stopped = True
        else:
            self.stopped = False
      


    def get_points_list(self, start=0, end=None):
        if not end:
            end  = self.npoints()
        res = []
        for i in range(start, end):
            res.append(self._trajectory[i][self.dimensions_used].tolist())
        return np.array(res)

    # TODO FIX
    def add_camera_point(self, x, y, t=-1, h=720, w=1280):
        if t < 0 and not self._trajectory.shape[0]:
            t = 0
        elif t < 0:
            t = self._trajectory[-1][2] + 1
        tx, ty = transform_point(x, y, w, h)
        self._trajectory = np.append(self._trajectory, [[tx, ty, t]], axis=0)

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
