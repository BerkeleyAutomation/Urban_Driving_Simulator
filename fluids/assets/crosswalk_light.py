from fluids.assets.shape import Shape
from fluids.consts import *

#RED = (200, 0, 0)
#YELLOW = (200, 200, 0),
#GREEN = (0, 200, 0)


class CrossWalkLight(Shape):
    def __init__(self, init_color="red", **kwargs):
        color = {"red":RED,
                 "green":GREEN}[init_color]
        self.timer = {"red":0,
                      "green":200}[init_color]
        Shape.__init__(self, xdim=10, ydim=30, color=color, **kwargs)

    def step(self, action):
        self.timer += 1
        if self.timer < 200:
            self.color = RED
        elif self.timer < 350:
            self.color = GREEN
        else:
            self.color = GREEN
        self.timer = self.timer % 400
        
    def get_future_color(self, time=60):

        return {RED:"red",
                YELLOW:"red",
                GREEN:"green"}[self.color]
