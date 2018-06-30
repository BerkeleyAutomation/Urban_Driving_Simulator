from fluids.assets.shape import Shape

class Sidewalk(Shape):
    def __init__(self, **kwargs):
        Shape.__init__(self, color=(150, 150, 150), **kwargs)
