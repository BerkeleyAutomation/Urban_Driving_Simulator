from fluids.assets.shape import Shape

class CrossWalkLight(Shape):
    def __init__(self, init_color="red", **kwargs):
        self.init_color = init_color
        Shape.__init__(self, xdim=10, ydim=10, color=(20, 150, 20), **kwargs)
