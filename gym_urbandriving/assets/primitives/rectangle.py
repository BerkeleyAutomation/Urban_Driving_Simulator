import numpy as np

SPRITE_DIR = "gym_urbandriving/visualizer/sprites/"

class Rectangle:
    def __init__(self, x, y, xdim, ydim, angle=0.0, sprite="no_texture.png"):
        """
        Initializes rectangle object.

        Args:
            x: float, starting x position.
            y: float, starting y position.
            angle: float, starting angle of car in degrees.
        """
        self.x = x
        self.y = y
        self.angle = angle
        self.xdim = xdim
        self.ydim = ydim
        self.sprite = SPRITE_DIR + sprite
        self.half_diag = np.sqrt(np.square(xdim) + np.square(ydim)) / 2.0

    def get_pos(self):
        """
        Returns x, y coordinates.

        Returns:
            x: float, x position.
            y: float, y position.
        """
        return self.x, self.y

    def get_primitive(self):
        return Rectangle
