from gym_urbandriving.assets import CrosswalkLight

class CrosswalkLightAgent:
    """
    Agent for controlling traffic one traffic light. 
    
    Attributes:
    -----------
    g_d : Duration of green light, in ticks
    r_d : Duration of red light, in ticks
    y_d : Duration of yellow light, in ticks
    
    g_d + y_d == r_d
    """
    transitions = {"white":"red",
                   "red":"white"}
    def __init__(self, agentnum=0, w_d=40, r_d=200):
        self.color_times = {"white":w_d,
                            "red":r_d}
        self.agentnum = agentnum

    def eval_policy(self, state):
        obj = state.dynamic_objects['crosswalk_lights'][str(self.agentnum)]
        assert(type(obj) == CrosswalkLight)
        if obj.time_in_color < self.color_times[obj.color]:
            return None
        return self.transitions[obj.color]
        
