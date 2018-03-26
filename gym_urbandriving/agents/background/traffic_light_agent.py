from gym_urbandriving.assets import TrafficLight

class TrafficLightAgent:
    """
    Agent for controlling traffic one traffic light. 
    
    Attributes:
    -----------
    g_d : Duration of green light, in ticks
    r_d : Duration of red light, in ticks
    y_d : Duration of yellow light, in ticks
    
    g_d + y_d == r_d
    """
    transitions = {"green":"yellow",
                   "yellow":"red",
                   "red":"green"}
    def __init__(self, agentnum=0, g_d=100, y_d=20, r_d=120):
        assert(g_d + y_d == r_d)
        self.color_times = {"green":g_d,
                            "yellow":y_d,
                            "red":r_d}
        self.agentnum = agentnum

    def eval_policy(self, state):
        obj = state.dynamic_objects['traffic_lights'][str(self.agentnum)]
        assert(type(obj) == TrafficLight)
        if obj.time_in_color < self.color_times[obj.color]:
            return None
        return self.transitions[obj.color]
        
