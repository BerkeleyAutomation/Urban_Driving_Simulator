from gym.envs.registration import register
from gym_urbandriving.envs import UrbanDrivingEnv
from gym_urbandriving.visualizer import PyGameVisualizer
from gym_urbandriving.state import PositionState


register(
    id='urbandriving-v0',
    entry_point='gym_urbandriving.envs:UrbanDrivingEnv'
)
