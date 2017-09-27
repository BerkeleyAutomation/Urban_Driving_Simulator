from gym_urbandriving.assets.primitives.rectangle import Rectangle

class Street(Rectangle):
    def __init__(self, x, y, xdim, ydim, angle=0.0, sprite="black.png"):
        Rectangle.__init__(self, x, y, xdim, ydim, angle=0.0, sprite=sprite);

