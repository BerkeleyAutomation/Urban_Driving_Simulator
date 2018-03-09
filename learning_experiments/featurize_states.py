from gym_urbandriving.utils.data_logger import DataLogger
from gym_urbandriving.assets.traffic_light import TrafficLight
from gym_urbandriving.utils.featurizer import Featurizer
import numpy as np
import shapely
import os
import gym_urbandriving as uds

FILES_PATH = "test_data/KIN_DYN_TRAJS"

N_ARCS = 9
ARC_DELTAS = [-1, -0.5, -0.25, -0.15, -0.1, 0, 0.1, 0.15, 0.25, 0.5, 1]
ARC_DELTAS = [i*np.pi/2 for i in ARC_DELTAS]
BEAM_DISTANCE = 300

LIGHT_ARC = np.pi / 16
LIGHT_DISTANCE = 300

print(ARC_DELTAS)

data_logger = DataLogger(FILES_PATH)



vis = uds.PyGameVisualizer((800, 800))
featurizer = Featurizer()

for index in range(1,2):
    loaded_rollout = data_logger.load_rollout(index)

    num_cars = loaded_rollout[1]['num_cars']
    goal_states = loaded_rollout[1]['goal_states']
    success = loaded_rollout[1]['success']
    agent_ids = loaded_rollout[1]['agent_ids']
    states = loaded_rollout[0]
    n_states = len(loaded_rollout[0])
    print(agent_ids, loaded_rollout[0][0])
    for i, agent_num in enumerate(agent_ids):
        for t in range(n_states-1):
            c_state = states[t]
            p_state = states[t-1]
            features = featurizer.featurize(c_state['state'], p_state['state'], agent_num)
            # action = c_state['action'][i]
            # state = c_state['state']
            # car = state.dynamic_objects[agent_num]

            # x, y, angle, vel = car.get_state()
            # #env = uds.UrbanDrivingEnv(visualizer=vis, init_state=state)
            # #env._render()
            vis.render(c_state['state'], [0, 1000, 0, 1000])

            # os.system('clear')
            # min_light_d = LIGHT_DISTANCE
            # min_light_state = 0

            # traffic_cone = shapely.geometry.Polygon([(x, y),
            #                                          (x + np.cos(-LIGHT_ARC+angle)*LIGHT_DISTANCE,
            #                                           y - np.sin(-LIGHT_ARC+angle)*LIGHT_DISTANCE),
            #                                          (x + np.cos(LIGHT_ARC+angle)*LIGHT_DISTANCE,
            #                                           y - np.sin(LIGHT_ARC+angle)*LIGHT_DISTANCE),])

            # for arc_delta in ARC_DELTAS:
            #     arc_angle = angle + arc_delta
            #     xd = x + np.cos(arc_angle)*BEAM_DISTANCE
            #     yd = y - np.sin(arc_angle)*BEAM_DISTANCE
            #     linestring = shapely.geometry.LineString([(x, y), (xd, yd)])
            #     #print(x, y, xd, yd)
            #     min_coll_d = BEAM_DISTANCE
            #     min_coll_type = None
            #     min_coll_vel = 0
            #     min_coll_angle = 0
            #     min_coll_acc = 0
            #     min_coll_ang_vel = 0


            #     for sobj in state.static_objects:
            #         if car.can_collide(sobj) and linestring.intersects(sobj.get_shapely_obj()):
            #             isect = list(linestring.intersection(sobj.get_shapely_obj()).coords)[0]
            #             d = distance((x, y), isect)
            #             if (d < min_coll_d):
            #                 min_coll_d = d
            #                 min_coll_type = type(sobj)
            #                 min_coll_vel = 0
            #                 min_coll_angle = 0
            #                 min_coll_acc = 0
            #                 min_coll_ang_vel = 0
            #     for did, dobj in enumerate(state.dynamic_objects):
            #         if car is not dobj and car.can_collide(dobj) and type(dobj) is not TrafficLight and linestring.intersects(dobj.get_shapely_obj()):
            #             isect = list(linestring.intersection(dobj.get_shapely_obj()).coords)[0]
            #             d = distance((x, y), isect)
            #             if (d < min_coll_d):
            #                 min_coll_d = d
            #                 min_coll_type = type(dobj)
            #                 min_coll_vel = dobj.vel
            #                 min_coll_angle = (angle - dobj.angle) % (2 * np.pi)
            #                 p_obj = p_state['state'].dynamic_objects[did]
            #                 min_coll_acc = dobj.vel - p_obj.vel
            #                 min_coll_ang_vel = (dobj.angle - p_obj.angle) % (2 * np.pi)
            #     print(min_coll_d, min_coll_type, 180 * min_coll_angle / np.pi, min_coll_vel, min_coll_ang_vel)
            # for dobj in state.dynamic_objects:
            #     if type(dobj) is TrafficLight and traffic_cone.intersects(dobj.get_shapely_obj()):
            #         d = distance((x, y), (dobj.x, dobj.y))
            #         if (d < min_light_d):
            #             min_light_d = d
            #             min_light_state = dobj.color
            # print(min_light_d, min_light_state)
            # print(x, y, vel)
