import numpy as np

SPRITE_DIR = "gym_urbandriving/visualizer/sprites/"


class Shape:
    def __init__(self, x, y, sprite="no_texture.png"):
        self.x = x
        self.y = y
        self.sprite = SPRITE_DIR + sprite

    def get_pos(self):
        return self.x, self.y

    def intersect(self, other):
        from gym_urbandriving.assets.primitives.rectangle import Rectangle
        from gym_urbandriving.assets.primitives.circle import Circle
        if self.primitive is Rectangle and other.primitive is Rectangle:
            # if np.linalg.norm([self.x - other.x, self.y - other.y]) > \
            #    self.halfdiag + other.halfdiag:
            #     return False
            other_corners = other.get_corners()
            has_collision = any([self.contains_point(point) for point in other_corners] + \
                                [other.contains_point(point) for point in self.get_corners()])
            return has_collision
        elif self.primitive is Circle and other.primitive is Circle:
            if np.sqrt(np.linalg.norm([self.x - other.x, self.y - other.y])) > \
               self.radius + other.radius:
                return False
            return True
