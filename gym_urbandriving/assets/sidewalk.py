import numpy as np
from gym_urbandriving.assets.primitives.rectangle import Rectangle
from gym_urbandriving.assets.pedestrian import Pedestrian

class Sidewalk(Rectangle):
    def __init__(self, x, y, xdim, ydim):
        Rectangle.__init__(self, x, y, xdim, ydim, sprite="gray.png");

    def generate_man(self, man_type=Pedestrian):
        man = man_type(0, 0, angle=self.angle)
        angle = np.radians(-self.angle)
        rotation_mat = np.array([[np.cos(angle), -np.sin(angle)],
                                 [np.sin(angle), np.cos(angle)]])
        x = np.random.uniform(0,
                              0+self.xdim/2-man.radius)
        y = np.random.uniform(0-self.ydim/2+man.radius,
                              0+self.ydim/2-man.radius)
        x, y = np.dot([x, y], rotation_mat.T)
        x, y = x+self.x, y+self.y
        man.x, man.y = x, y
        return man


