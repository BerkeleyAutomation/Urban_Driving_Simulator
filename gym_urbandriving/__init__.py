from gym.envs.registration import register
from gym_urbandriving.envs import UrbanDrivingEnv
from gym_urbandriving.visualizer import PyGameVisualizer
from gym_urbandriving.state import SimpleIntersectionState
from gym_urbandriving.state import SimpleTIntersectionState
from gym_urbandriving.state import ArenaState
from gym_urbandriving.state import AngledIntersectionState


register(
    id='urbandriving-v0',
    entry_point='gym_urbandriving.envs:UrbanDrivingEnv'
)
