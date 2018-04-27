import six
import numpy as np

def default_reward_function(state):
    """
    Default reward function for controlling multiple cars.
    """

    reward = 0
    controlled_collisions = state.get_collisions()[2]

    for ck, controlled_car in six.iteritems(state.dynamic_objects['controlled_cars']):
        carx = controlled_car.x
        cary = controlled_car.y

        goalx = controlled_car.destination[0]
        goaly = controlled_car.destination[1]
        d_to_goal = np.sqrt((carx - goalx) ** 2 + (cary - goaly) ** 2)
        for coll in controlled_collisions:
            if ck == coll[0]:
                reward = reward - 200
                break
        else:
            reward = reward - d_to_goal
    return reward
