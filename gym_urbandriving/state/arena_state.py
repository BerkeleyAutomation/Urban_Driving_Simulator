from gym_urbandriving.state.state import PositionState
from gym_urbandriving.assets import Street, Car
import numpy as np

class ArenaState(PositionState):
    static_objects = [Street(500, 500, 1000, 1000)]

    def __init__(self, ncars=4, nped=0):
        self.ncars = ncars
        PositionState.__init__(self)
        self.randomize()

    def randomize(self):
        self.dynamic_objects = []
        while len(self.dynamic_objects) < self.ncars:
            angle = np.random.uniform(0, 2*np.pi)
            rotation_mat = np.array([[np.cos(angle), -np.sin(angle)],
                                     [np.sin(angle), np.cos(angle)]])
            x, y = np.dot([400, 0], rotation_mat.T)
            angle_offset = np.random.uniform(-30, 30)
            car = Car(x+500, y+500, angle=angle,
                      dynamics_model="kinematic")
            car.vel = 0
            if not any([car.collides(obj) for obj in self.static_objects+self.dynamic_objects]):
                self.dynamic_objects.append(car)
       
