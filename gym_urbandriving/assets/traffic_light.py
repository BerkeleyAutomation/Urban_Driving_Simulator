from gym_urbandriving.assets.primitives.rectangle import Rectangle
from gym_urbandriving.assets.primitives.shape import Shape

class TrafficLight(Rectangle):
    """
    Represents a static traffic light in the scene
    
    Parameters
    ----------
    x : float
        Starting x coordinate of light
    y : float
        Starting y coordinate of light
    angle : float
        Starting angle of light in degrees
    """
    colors = {"green" : "traffic_green.png",
              "yellow" : "traffic_yellow.png",
              "red" : "traffic_red.png"}
    def __init__(self, x, y, angle, initial_color="green"):
        Rectangle.__init__(self, x, y, 15, 15, angle)
        self.time_in_color = 0
        self.color = initial_color

    def step(self, action):
        self.time_in_color += 1
        if action is not None:
            assert(action in self.colors)
            if (action is not self.color):
                self.time_in_color = 0
            self.color = action

    def can_collide(self, other):
        return False

    def get_sprite(self):
        return Shape.SPRITE_DIR + self.colors[self.color]
        
