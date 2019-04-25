from fluids.assets.shape import Shape
from fluids.consts import *




class TrafficLight(Shape):
    def __init__(self, init_color="red", **kwargs):
        self.init_color = init_color
        color = {"red":RED,
                 "green":GREEN,
                 "yellow":YELLOW}[init_color]
        self.timer = {"red":0,
                      "green":200,
                      "yellow":350}[init_color]

        Shape.__init__(self, xdim=20, ydim=60, color=color, **kwargs)


    def step(self, action):
        self.timer += 1
        if self.timer < 200:
            self.color = RED
        elif self.timer < 350:
            self.color = GREEN
        else:
            self.color = YELLOW
        self.timer = self.timer % 400

    def get_future_color(self, time=60):

        return {RED:"red",
                YELLOW:"red",
                GREEN:"green"}[self.color]
        
