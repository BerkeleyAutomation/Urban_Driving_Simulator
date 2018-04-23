import numpy as np
from gym_urbandriving.utils import Trajectory
from gym_urbandriving.actions import VelocityAction

"""
Test our trajectory class for various modes. 
"""

for t in range(100):
    global_mode='xyvacst'

    # choose dimension of our trajectory randomly
    dimension = np.random.randint(1,6)

    # build our mode randomly
    indices = np.random.choice(6,dimension,replace=False)
    mode = ''
    for i in indices:
        mode += global_mode[i]

    traj_test = Trajectory(mode = mode)

    # test is not empty
    traj_test.add_point(np.ones(dimension))
    assert(not traj_test.is_empty())

    # insert a bunch of elements
    expected_npoints = np.random.randint(5,100) + 1
    for j in range(expected_npoints-1):
        traj_test.add_point(np.random.uniform(0,1,dimension))


    assert(traj_test.npoints() == expected_npoints)

    # insert last element with distinct elements
    traj_test.add_point(np.arange(dimension))

    assert(not traj_test.is_empty())
    assert(traj_test.first() == np.ones(dimension)).all()
    assert(traj_test.last() == np.arange(dimension)).all()

    traj_test.add_interpolated_t()
    dimension += 1

    expected_t = np.random.randint(0, expected_npoints)

    point_t = traj_test.get_next_point(expected_t)
    assert point_t[-1] == expected_t

    # pop elements off making sure they are correctly shaped and populated
    while(not traj_test.is_empty()):
        p = traj_test.pop()
        assert p.shape[0] == dimension
        assert not np.nan in p
        assert p[-1] == expected_t
        expected_t += 1

    # check last element popped is the same as the last element added
    assert (p[:-1] == np.arange(dimension-1)).all()

    # assert everything popped off
    assert(traj_test.is_empty())


mode = 'xyvacst'
traj_test = Trajectory(mode = mode)
arr1 = np.random.uniform(0,1,7)
traj_test.add_point(arr1)
arr2 = np.random.uniform(0,1,7)
traj_test.add_point(arr2)
assert (traj_test.get_matrix() == np.matrix([arr1, arr2])).all()
assert (traj_test.get_renderable_points() == np.matrix([arr1[:2], arr2[:2]])).all()

traj_test.stopped == True
try:
    traj_test.set_vel(None)
except Exception as e:
    assert(False)

traj_test.set_vel(VelocityAction(5.0))
assert(traj_test.get_vel().get_value() == 5.0)
assert(traj_test.stopped == False)

traj_test.set_vel(VelocityAction(0.0))
assert(traj_test.get_vel().get_value() == 0.0)
assert(traj_test.stopped == True)
