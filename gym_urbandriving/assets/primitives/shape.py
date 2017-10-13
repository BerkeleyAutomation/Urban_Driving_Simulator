import numpy as np

SPRITE_DIR = "gym_urbandriving/visualizer/sprites/"


class Shape:
    def __init__(self, x, y, sprite="no_texture.png", static=False):
        self.x = x
        self.y = y
        self.sprite = SPRITE_DIR + sprite
        self.static = static

    def get_pos(self):
        return np.array([self.x, self.y])

    def intersect(self, other):
        from gym_urbandriving.assets.primitives.rectangle import Rectangle
        from gym_urbandriving.assets.primitives.circle import Circle

        types = {self.primitive, other.primitive}
        center_dist = np.linalg.norm([self.x - other.x, self.y - other.y])

        if types == {Rectangle, Rectangle}:
            min_dist = min(self.xdim, self.ydim)/2 + min(self.xdim, self.ydim)/2
            if center_dist > self.halfdiag + other.halfdiag:
                return False
            if center_dist < min_dist:
                return True

            for point in self.get_corners():
                if other.contains_point(point):
                    return True
            for point in other.get_corners():
                if self.contains_point(point):
                    return True
            return False
        elif types == {Circle, Circle}:
            if center_dist > self.radius + other.radius:
                return False
            return True
        elif types == {Rectangle, Circle}:
            rect = self if self.primitive is Rectangle else other
            circle = self if self.primitive is Circle else other

            if (center_dist > rect.halfdiag + circle.radius):
                return False

            angle = np.radians(rect.angle+45)
            A = (circle.x + circle.radius*np.cos(angle),
                 circle.y + circle.radius*np.sin(angle))
            B = (circle.x + circle.radius*np.cos(angle+np.pi/2),
                 circle.y + circle.radius*np.sin(angle+np.pi/2))
            C = (circle.x + circle.radius*np.cos(angle+np.pi),
                 circle.y + circle.radius*np.sin(angle+np.pi))
            D = (circle.x + circle.radius*np.cos(angle-np.pi/2),
                 circle.y + circle.radius*np.sin(angle-np.pi/2))

            circ_corners = [A, B, C, D]
            rect_corners = rect.get_corners()

            for point in rect_corners:
                if circle.contains_point(point):
                    return True
            for point in circ_corners:
                if rect.contains_point(point):
                    return True
            return False
