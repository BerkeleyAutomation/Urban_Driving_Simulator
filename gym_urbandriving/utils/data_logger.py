from gym_urbandriving.state.state import PositionState
from gym_urbandriving.assets import Terrain, Lane, Street, Sidewalk,\
    Pedestrian, Car, TrafficLight
import numpy as np
import IPython
import os

###Class created to store relevant information for learning at scale

class DataLogger():

    def __init__(self,file_path):

        self.data = []
        self.rollout_info = {}
        self.file_path = file_path

        
        if not os.path.exists(self.file_path):
            os.makedirs(self.file_path)


    def next_rollout(self):
        """
        return: the String name of the next new potential rollout
        (i.e. do not overwrite another rollout)
        """
        i = 0

        path = self.file_path+'/rollout_'+str(i)+'.npy'


        while os.path.isfile(path):
            i += 1
            path = self.file_path + '/rollout_'+str(i) +'.npy'
            print i

        return i



    def save_rollout(self,rollout):

        ###ADD

        data = [rollout,self.rollout_info]

        path_index = self.next_rollout()


        np.save(self.file_path+'/rollout_'+str(path_index),data)

        self.rollout_info = {}




    def log_info(self,name,info):

        self.rollout_info[name] = info


    def load_rollout(self, index):
        return np.load(self.file_path+'/rollout_' + str(index) + '.npy')



