import numpy as np
import os
import glob
from numpy.random import uniform
import matplotlib.pyplot as plt

plt.style.use('ggplot')

class Plotter():
    """
    Class to plot performance of various Imitation Learning Methods
    """
    def __init__(self,file_path):
        self.file_path = file_path

        if not os.path.exists(self.file_path+'/plots'):
            os.makedirs(self.file_path+'/plots')

    def save_plots(self,stats):
        '''
        Save the plots to measure different aspects of the experiment

        Paramters
        -----------
        stats: list of dict
            Contains the measured statistics 
        '''

        reward_sup = []
        reward_robot = []

        loss_sup = []
        loss_robot = []

        loss_sup = []
        train_sup = []

        for i in range(len(stats)):

            reward_sup.append(stats[i]['reward_sup'])
            reward_robot.append(stats[i]['reward_robot'])

            loss_sup.append(stats[i]['loss_sup'])
            loss_robot.append(stats[i]['loss_robot'])

            
            train_sup.append(stats[i]['train_sup'])

        plt.plot(reward_sup,label = 'R.S.' )
        plt.plot(reward_robot,label = 'R.R.' )
        plt.legend()

        plt.savefig(self.file_path+'/plots/reward.png')
        plt.clf()

        plt.plot(loss_sup,label = 'L.S.' )
        plt.plot(loss_robot,label = 'L.R.' )
        plt.legend()

        plt.savefig(self.file_path+'/plots/covariate_shift.png')
        plt.clf()

        plt.plot(loss_sup,label = 'L.S.' )
        plt.plot(train_sup,label = 'T.S.' )
        plt.legend()

        plt.savefig(self.file_path+'/plots/generalization.png')
        plt.clf()




