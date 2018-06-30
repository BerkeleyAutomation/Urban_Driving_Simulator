from fluids.assets.shape import Shape

class SidewalkSquare(Shape):
    def __init__(self, **kwargs):
        Shape.__init__(self, color=(170, 170, 170), **kwargs)
