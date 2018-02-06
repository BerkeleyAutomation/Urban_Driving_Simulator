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

class Trajectory(object):
    def __init__(self):
        self._trajectory = np.zeros(0, 3)
        # Path in 2D space. Shape n, 3, where n is number of points
        # x, y, t is the other dimension
        
        
