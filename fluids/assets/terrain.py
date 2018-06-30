from fluids.assets.shape import Shape

class Terrain(Shape):
    def __init__(self, **kwargs):
        Shape.__init__(self, color=(150, 200, 150), **kwargs)
