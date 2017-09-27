import numpy as np

SPRITE_DIR = "gym_urbandriving/visualizer/sprites/"


class Shape:
    def __init__(self, x, y, sprite="no_texture.png"):
        self.x = x
        self.y = y
        self.sprite = SPRITE_DIR + sprite

    def get_pos(self):
        return np.array([self.x, self.y])

    def intersect(self, other):
        from gym_urbandriving.assets.primitives.rectangle import Rectangle
        from gym_urbandriving.assets.primitives.circle import Circle

        types = {self.primitive, other.primitive}
        if types == {Rectangle, Rectangle}:
            if np.linalg.norm([self.x - other.x, self.y - other.y]) > \
               self.halfdiag + other.halfdiag:
                return False
            other_corners = other.get_corners()
            has_collision = any([self.contains_point(point) for point in other_corners] + \
                                [other.contains_point(point) for point in self.get_corners()])
            return has_collision
        elif types == {Circle, Circle}:
            if np.linalg.norm([self.x - other.x, self.y - other.y]) > \
               self.radius + other.radius:
                return False
            return True
        elif types == {Rectangle, Circle}:
            rect = self if self.primitive is Rectangle else other
            circle = self if self.primitive is Circle else other

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

            has_collision = any([circle.contains_point(point) for point in rect_corners] + \
                                [rect.contains_point(point) for point in circ_corners])

            return has_collision
