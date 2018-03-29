from gym_urbandriving.assets.street import Street
from gym_urbandriving.assets.primitives import Rectangle, Polygon
from gym_urbandriving.assets.car import Car
import numpy as np

class Lane(Polygon):
    """
    Represents a lane of road. Lanes have directionality, so cars should drive in the
    right direction. Default construction creates a rectangular block.

    Parameters
    ----------
    x : float
       Upper left x coordinate of the lane block
    y : float
       Upper left y coordinate of the lane block
    xdim : float
       Width of the lane block
    ydim : float
       Height of the lane block
    angle ; float
       In degrees, the rotation of the lane block. The correct direction of travel along this lane.
    points : list
       List of XY coordinates specifying edge points of a polygon.
       If specified, lane will be constructed as a polygon.
    curvature : list
       If specified, generates a curved road segment with this arc angle, centered at x, y, and with inner and outer radii
    inner_r, outer_r : float
       Use with curvature argument to generated curved road segment.
    """

    def __init__(self, x=0, y=0, xdim=0, ydim=0, angle=0.0, angle_deg=0, points=[], curvature=0, inner_r=0, outer_r=0):
        """
        Initializes lane as a Polygon object

        """
        angle = np.deg2rad(angle_deg % 360.) if angle_deg else angle
        if not len(points) and not curvature:
            a = angle % (2*np.pi)
            a = -a
            corner_offsets = np.array([xdim / 2.0, ydim / 2.0])
            centers = np.array([x, y])
            signs = np.array([[1,1], [1,-1], [-1,-1], [-1,1]])
            corner_offsets = signs * corner_offsets
            rotation_mat = np.array([[np.cos(a), -np.sin(a)],
                                     [np.sin(a), np.cos(a)]])
            points = np.dot(corner_offsets, rotation_mat.T) + centers
        if not len(points) and curvature:
            assert(inner_r < outer_r)
            angles = [i*curvature/10 + angle for i in range(11)]
            outers = [(outer_r*np.cos(a)+x, -outer_r*np.sin(a)+y) for a in angles]
            inners = [(inner_r*np.cos(a)+x, -inner_r*np.sin(a)+y) for a in angles]
            points = outers + inners[::-1]
            angle = (curvature/2 + np.pi/2 + angle) % (2*np.pi)
        Polygon.__init__(self, points, angle, color=(40, 40, 40))


    def generate_car(self, car_model="kinematic"):
        """
        Creates a car on this lane ready to drive into the intersection

        Parameters
        ----------
        car_type : "kinematic" or "point" or "reeds_shepp"
            Specifies dynamics model for the car
        Returns
        -------
        Car
            Generated Car object
        """

        x = np.random.uniform(self.minx+50.,
                              self.maxx-50.)
        y = np.random.uniform(self.miny+50.,
                              self.maxy-50.)
        car = Car(x, y, angle=self.angle+np.random.uniform(-0.1, 0.1),
                  dynamics_model=car_model)
        return car


    def side_of_road(self,point):
      
      if self.angle%np.pi < 1e-5:
        y_dif = point[1] - ((self.miny +self.maxy)/2.0)

        if y_dif > 0:
          return "RIGHT"
        else: 
          return "LEFT"

      if self.angle%np.pi > 1e-5:
        x_dif = point[0] - ((self.minx +self.maxx)/2.0)

        if x_dif > 0:
          return "LEFT"
        else: 
          return "RIGHT"     






