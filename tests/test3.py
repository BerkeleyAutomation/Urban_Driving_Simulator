import numpy as np
from gym_urbandriving.planning import Trajectory

"""
Test our trajectory class for various modes. 
"""

for t in range(500):
    global_mode='xyvacst'

    # choose dimension of our trajectory randomly
    dimension = np.random.randint(1,7)

    # build our mode randomly
    indices = np.random.choice(7,dimension,replace=False)
    mode = ''
    for i in indices:
        mode += global_mode[i]

    traj_test = Trajectory(mode = mode)

    # test is not empty
    traj_test.add_point(np.ones(dimension))
    assert(not traj_test.is_empty())

    # insert a bunch of elements
    for j in range(np.random.randint(5,100)):
        traj_test.add_point(np.random.uniform(0,1,dimension))

    # insert last element with distinct elements
    traj_test.add_point(np.arange(dimension))
    assert(not traj_test.is_empty())

    # pop elements off making sure they are correctly shaped and populated
    while(not traj_test.is_empty()):
        p = traj_test.pop()
        assert p.shape[0] == dimension
        assert not np.nan in p

    # check last element popped is the same as the last element added
    assert (p == np.arange(dimension)).all()

    # assert everything popped off
    assert(traj_test.is_empty())