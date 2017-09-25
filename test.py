import gym
import gym_urbandriving as uds
import cProfile

def f():
    
    vis = uds.PyGameVisualizer((800, 800))
    env = uds.UrbanDrivingEnv(visualizer=vis)
    while(True):
        state, reward, done = env._step(None)
        env._render()
        if done:
            print("done")
            env._reset()

cProfile.run('f()', 'stats')
