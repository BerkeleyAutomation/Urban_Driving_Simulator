from fluids.assets.shape import Shape

class PedCrossing(Shape):
    def __init__(self, **kwargs):
        Shape.__init__(self, color=(0xf7, 0xf7, 0xf7), **kwargs)
        self.in_waypoints = []
        self.out_waypoints = []
