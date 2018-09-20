import gym
import gym_fluids

env = gym.make("fluids-v2")
env.reset()
action = [0, 0]

successes = 0
n = 10
for t in range(n):
    reward = 0
    for i in range(100):
        obs, rew, done, info = env.step(action)
        reward += rew
        assert(obs.shape == (400, 400, 3))
        env.render()
        action = gym_fluids.agents.fluids_supervisor(obs, info)
    if (reward) >= 0:
        successes += 1
assert(successes / n > 0.8)


del(env)

env = gym.make("fluids-vel-v2")
env.reset()
action = [0]
for i in range(100):
    obs, rew, done, info = env.step(action)
    reward += rew
    assert(obs.shape == (400, 400, 3))
    env.render()
    action = gym_fluids.agents.fluids_supervisor(obs, info)

assert(reward >= 0)
