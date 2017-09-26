from gym_urbandriving.assets.street import Street
from gym_urbandriving.assets.primitives import Rectangle


class Lane(Street):
    def __init__(self, x, y, xdim, ydim, angle=0.0):
        Rectangle.__init__(self, x, y, xdim, ydim, angle=angle, sprite="lane.png");
