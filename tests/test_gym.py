import gym
import gym_fluids

env = gym.make("fluids-v2")
env.reset()

success = False
for j in range(2):
    env.reset()
    t_success = True
    for i in range(10):
        obs, rew, done, _ = env.step([0, 0])
        assert(obs.shape == (400, 400, 3))
        if rew != 0:
            t_success = False
        env.render()
    if t_success:
        success = True

assert(success)


del(env)

env = gym.make("fluids-vel-v2")
env.reset()
env.step([0])
env.render()
