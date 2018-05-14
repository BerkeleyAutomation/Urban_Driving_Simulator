from copy import deepcopy
import gym_urbandriving as uds
from gym_urbandriving.actions import VelocityAction
from gym_urbandriving.utils.featurizer import Featurizer
import IPython
import numpy as np
import os

class VelocityNeuralPlanner:
        def __init__(self, lookahead=10):

                basedir = os.path.dirname(__file__)
                file_path = basedir+'/models/model.npy'
                data =  np.load(file_path)
                featurizer_config = {"goal_position":False}
                self.model = data.all()
                self.featurizer = Featurizer(config_data=featurizer_config)

        def plan(self, state, agent_num,type_of_agent = "background_cars"):

                feature = self.featurizer.featurize(state,str(agent_num),type_of_agent)
                action = self.model.predict(np.array([feature]))

                return VelocityAction(action[0])
