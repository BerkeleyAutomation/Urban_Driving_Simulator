import gym
import gym_urbandriving as uds

vis = uds.PyGameVisualizer((800, 800))
env = uds.UrbanDrivingEnv(visualizer=vis)
while(True):
    env._render()
    env._step(None)
