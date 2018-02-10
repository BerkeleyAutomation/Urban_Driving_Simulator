import numpy as np
from gym_urbandriving.utils import Trajectory

"""
Test our trajectory class for various modes. 
"""

for t in range(500):
    global_mode='xyvacst'
    dimension = np.random.randint(1,7)
    indices = np.random.choice(7,dimension,replace=False)
    mode = ''
    for i in indices:
        mode += global_mode[i]

    traj_test = Trajectory(mode = mode)

    traj_test.add_point(np.ones(dimension))
    assert(not traj_test.is_empty())

    for j in range(np.random.randint(5,100)):
        traj_test.add_point(np.random.uniform(0,1,dimension))

    traj_test.add_point(np.arange(dimension))
    assert(not traj_test.is_empty())

    while(not traj_test.is_empty()):
        p = traj_test.pop()
        assert p.shape[0] == dimension
        assert not np.nan in p

    assert (p == np.arange(dimension)).all()

    assert(traj_test.is_empty())