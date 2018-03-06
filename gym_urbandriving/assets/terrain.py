import numpy as np
from gym_urbandriving.assets.primitives import Rectangle, Polygon
import shapely.geometry

class Terrain(Polygon):
    """
    Represents a square of impassable terrain
    
    Parameters
    ----------
    points : list
       List of X-Y tuples in ccw order describing vertices of the polygon
    """
    def __init__(self, x, y, xdim=0, ydim=0, points=[], radius=0, excludes=[]):
        if not points and radius==0:
            ulx, uly, lrx, lry = x-xdim/2, y-ydim/2, x+xdim/2, y+ydim/2
            points = [(ulx, uly), (lrx, uly), (lrx, lry), (ulx, lry)]
        elif not points:
            angles = [i*np.pi*2/100 for i in range(100)]
            points = [(radius*np.cos(a)+x, -radius*np.sin(a)+y) for a in angles]

        for ex in excludes:
            obj = shapely.geometry.Polygon(points).difference(ex.get_shapely_obj())
            p = obj.exterior.coords
            points = np.asarray(p)
        
        Polygon.__init__(self, points, color=(255, 255, 255))
