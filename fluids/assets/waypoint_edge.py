import numpy as np
import shapely
from fluids.assets.shape import Shape


class WaypointEdge(Shape):
    def __init__(self, wp0, wp1, buff=10, **kwargs):

        line = shapely.geometry.LineString([(wp0.x, wp0.y), (wp1.x, wp1.y)]).buffer(buff)
        points = np.array(list(zip(*(line).exterior.coords.xy)))
        #angle = np.arctan2([wp0.y - wp1.y], [wp0.x - wp1.x])[0]
        angle = 0
        super(WaypointEdge, self).__init__(angle=angle, points=points, color=(200, 200, 200), **kwargs)
        self.in_p  = wp0
        self.out_p = wp1
        
