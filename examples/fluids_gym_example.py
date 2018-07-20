import gym
import gym_fluids

env = gym.make("fluids-v2")

env.reset()

action = [0, 0]
reward = 0
while True:
    obs, rew, done, info = env.step(action)
    reward += rew

    env.render()
    print(rew, action)
    action = gym_fluids.agents.fluids_supervisor(obs, info)
