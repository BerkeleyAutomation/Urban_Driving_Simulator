import numpy as np

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
tf_mat = skimage.transform.ProjectiveTransform()
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
    def __init__(self, target='car'):
        self._trajectory = np.zeros(0, 3)
        self.target = target
        # Path in 2D space. Shape n, 3, where n is number of points
        # x, y, t is the other dimension

    def get_points(self):
        # Return 2d point list
        return self._trajectory

    def add_point(self, x, y, t=-1):
        if t < 0 and not self._trajectory.shape[0]:
            t = 0
        elif t < 0:
            t = self._trajectory[-1][2] + 1

        self._trajectory = np.append(self._trajectory, [[x, y, t]], axis=0)

    def add_camera_point(self, x, y, t=-1, h=720, w=1280):
        if t < 0 and not self._trajectory.shape[0]:
            t = 0
        elif t < 0:
            t = self._trajectory[-1][2] + 1
        tx, ty = transform_point(x, y, w, h)
        self._trajectory = np.append(self._trajectory, [[tx, ty, t]], axis=0)
