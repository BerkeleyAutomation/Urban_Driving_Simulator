from gym.envs.registration import register
from gym_urbandriving.envs import *
from gym_urbandriving.visualizer import *


register(
    id='urbandriving-v0',
    entry_point='gym_urbandriving.envs:UrbanDrivingEnv'
)
