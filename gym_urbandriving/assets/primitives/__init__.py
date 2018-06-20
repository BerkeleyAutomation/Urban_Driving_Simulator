

from gym_urbandriving.assets.primitives.rectangle import Rectangle
from gym_urbandriving.assets.primitives.polygon import Polygon
from gym_urbandriving.assets.primitives.circle import Circle
from gym_urbandriving.assets.primitives.dynamic_shape import DynamicShape
try:
    from gym_urbandriving.assets.primitives.integrator_c import Model
except ImportError:
    a = 1
