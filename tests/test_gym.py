import gym
import gym_fluids

env = gym.make("fluids-v2")
env.reset()

for i in range(10):
    obs, rew, done, _ = env.step([0, 0])
    assert(obs.shape == (400, 400, 3))
    assert(rew == 0)
    env.render()
    

del(env)

env = gym.make("fluids-vel-v2")
env.reset()
env.step([0])
env.render()
