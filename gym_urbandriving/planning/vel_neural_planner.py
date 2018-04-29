from copy import deepcopy
import gym_urbandriving as uds
from gym_urbandriving.actions import VelocityAction
from gym_urbandriving.utils.featurizer import Featurizer
import IPython
import numpy as np

class VelocityNeuralPlanner:
    def __init__(self, lookahead=10):
        file_path = 'gym_urbandriving/planning/models/model.npy'
        data =  np.load(file_path)
        self.model = data.all()
        self.featurizer = Featurizer()

    def plan(self, state, agent_num,type_of_agent = "background_cars"):
        
        feature = self.featurizer.featurize(state,str(agent_num),type_of_agent)
        action = self.model.predict(np.array([feature]))

        return VelocityAction(action[0])