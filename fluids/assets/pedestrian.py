from fluids.assets.shape import Shape

class Pedestrian(Shape):
    def __init__(self):
        Shape.__init__(self, color=(0, 150, 150), **kwargs)
