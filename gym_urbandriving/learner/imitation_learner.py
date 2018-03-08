from gym_urbandriving.state.state import PositionState
from gym_urbandriving.assets import Terrain, Lane, Street, Sidewalk,\
    Pedestrian, Car, TrafficLight
import numpy as np
import os
import glob
from sklearn.tree import DecisionTreeClassifier
from numpy.random import uniform
import numpy.linalg as LA


###Class created to store relevant information for learning at scale

class IL():

    def __init__(self,file_path, num_cars=2):

        self.data = []
        self.rollout_info = {}
        self.file_path = file_path
        self.num_cars = num_cars

    def load_data(self):
        """
        Loads the data from the specified path 

        Returns
        ----------
        path: list
            Containing the rollouts
        """
        i = 0

        paths = glob.glob(self.file_path+'/rollout_*')
        self.rollouts = []
        
        for path in paths:
            data_point = np.load(path)
            self.rollouts.append(data_point)

        return paths


    def train_model(self):

        """
        Trains a model on the loaded data, for know its a sklearn model
        """

        self.X_train = []
        self.Y_train = []

        self.X_test = []
        self.Y_test = []

        #We are currently using a decision tree, however this can be quite modular
        self.model = DecisionTreeClassifier()


        for rollout in self.rollouts:

            if uniform() > 0.2:
                train = True
            else:
                train = False

            goal_state = rollout[1]['goal_states']
            success = rollout[1]['success']
            num_cars = rollout[1]['num_cars']

            for datum in rollout[0]:

                state = datum['state']
                actions = self.make_action(datum['target_velocities'])

                

                if None in actions:
                    continue # one car did not take a valud action

                states = self.make_state(num_cars,state,goal_state)

              
                if train:
                    for s_ in states:
                        self.X_train.append(s_)
                    for a_ in actions:
                        self.Y_train.append(a_)
                else:
                    for s_ in states:
                        self.X_test.append(s_)
                    for a_ in actions:
                        self.Y_test.append(a_)

        self.model.fit(self.X_train,self.Y_train) 
        


    def make_state(self,num_cars,state,goal_state):
        """
        Constructs the state space to be learned on, which is a concatentation of the
        current state and the goal state

        Parameters
        ----------
        state: state of the enviroment
        goal_state: list of [x,y,velocity, theta] states

        Returns
        ------------
        numpy array of teh concatenated state for all agents
        """
        s_ = []
        for i in range(num_cars):
            s = np.array(state.dynamic_objects[i].get_state())

            s_.append(s)
            


        return s_

    def make_action(self,action):
        """
        Makes an action for sklearn to use

        Parameters
        ----------
        action: list of actions

        Returns
        ------------
        numpy array of of actions
        """
        binary_list = []
        for a in action:
            if a == 4:
                binary_list.append(1)
            else:
                binary_list.append(0)


        return binary_list

    def unmake_action(self,actions):
        """
        Converst the output of the model to an action usable by the simulator

        Parameters
        ----------
        action: numpy array

        Returns
        ------------
        list of each action for the agent
        """
        velocities = []
        for i in range(len(actions)):

            if np.abs(actions[i] - 4) < 1e-5:
                velocities.append(4)
            else:
                velocities.append(0)

        return velocities


    def get_train_error(self):
        """
        Reports the training error of the model

        Returns
        ------------
        float specifying L2 error
        """

        avg_err = 0.0

        for i in range(len(self.X_train)):

            x = np.array([self.X_train[i]])
            y = self.Y_train[i]

            y_ = self.model.predict(x)

            if not y_ == y:
                avg_err += 1.0

        return avg_err/float(len(self.X_train))


    def get_cs(self,evaluations):
        """
        Report the on-policy surrogate loss to measure covariate shift

        Returns
        ------------
        float specifying L2 error
        """

        count = 0.0
        avg_err = 0.0

        for rollout in evaluations:
            for datum in rollout:

                robot_action = self.make_action(datum['target_velocities_learner'])
                sup_action = self.make_action(datum['target_velocities_sup'])
                
                for i in range(len(robot_action)):
                    r_a_ = robot_action[i]
                    s_a_ = sup_action[i]

                    if not r_a_ == s_a_:
                        avg_err += 1.0

                
                count += 1.0


        return avg_err/count



    def get_test_error(self):
        """
        Reports the test error of the model

        Returns
        ------------
        float specifying L2 error
        """


        avg_err = 0.0

        for i in range(len(self.X_test)):

            x = np.array([self.X_test[i]])
            y = self.Y_test[i]

            y_ = self.model.predict(x)

            if not y_ == y:
                avg_err += 1.0
            

        if len(self.X_test) == 0:
            return avg_err

        return avg_err/float(len(self.X_test))




    def eval_model(self,num_cars, state,goal_state):
        """
        Evaluates model, which is used in execution 
        
        Parameters
        ----------
        state: state of the enviroment
        goal_state: list of [x,y,velocity, theta] states

        Returns
        ------------
        list of each action for the agent
        """


        states = self.make_state(num_cars,state,goal_state)

        actions = []

        for s_ in states:
            actions.append(self.model.predict(np.array([s_])))


        return self.unmake_action(actions)





