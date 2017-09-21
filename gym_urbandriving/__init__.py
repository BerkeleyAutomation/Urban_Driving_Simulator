from gym.envs.registration import register

register(
    id='urbandriving-v0',
    entry_point='gym_urbandriving.envs:UrbanDrivingEnv'
)
