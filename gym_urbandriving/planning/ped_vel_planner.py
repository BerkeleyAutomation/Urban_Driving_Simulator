import numpy as np

class PedestrianVelPlanner:
    def __init__(self, lookahead=10):
        pass


    def plan(self, state, agent_num):
        """
        Moves pedestrian 5 forwards, then checks for collision. If no, return high vel term. 
        """
        agent_x = state.dynamic_objects[agent_num].x
        agent_y = state.dynamic_objects[agent_num].y
        agent_angle = state.dynamic_objects[agent_num].angle

        state.dynamic_objects[agent_num].x = agent_x + 5*np.cos(agent_angle)
        state.dynamic_objects[agent_num].y = agent_y - 5*np.sin(agent_angle)

        if state.collides_any(agent_num):
            return 0
        return 2
