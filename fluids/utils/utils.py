import numpy as np

def rotation_array(angle):
    cosa = np.cos(angle)
    sina = np.sin(angle)
    return np.array([[cosa, -sina],
                     [sina, cosa]])
