from gym_urbandriving.state.state import PositionState
from gym_urbandriving.assets import Terrain, Lane, Street, Sidewalk,\
    Pedestrian, Car, TrafficLight
import numpy as np
import IPython
import os
import glob
from sklearn.tree import DecisionTreeRegressor
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
		return: the String name of the next new potential rollout
		(i.e. do not overwrite another rollout)
		"""
		i = 0

		paths = glob.glob(self.file_path+'/rollout_*')
		self.rollouts = []
		
		for path in paths:
			data_point = np.load(path)
			self.rollouts.append(data_point)

		return paths

	def load_eval_data(self):
		"""
		return: the String name of the next new potential rollout
		(i.e. do not overwrite another rollout)
		"""
		i = 0

		paths = glob.glob(self.file_path+'/rollout_*')
		self.rollouts = []
		
		for path in paths:
			data_point = np.load(path)
			self.rollouts.append(data_point)

		return paths


	def train_model(self):

		###ADD

		self.X_train = []
		self.Y_train = []

		self.X_test = []
		self.Y_test = []

		self.model = DecisionTreeRegressor()


		for rollout in self.rollouts:

			if uniform() > 0.2:
				train = True
			else:
				train = False

			goal_state = rollout[1]['goal_states']
			success = rollout[1]['success']

			for datum in rollout[0]:

				state = datum['state']
				action = self.make_action(datum['action'])

				a_ = action.flatten()

				s_ = self.make_state(state,goal_state)

				if train:
					self.X_train.append(s_)
					self.Y_train.append(a_)
				else:
					self.X_test.append(s_)
					self.Y_test.append(a_)


		self.model.fit(self.X_train,self.Y_train) 
		


	def make_state(self,state,goal_state):
		s_ = []
		for i in range(self.num_cars):
			s_.append(state.dynamic_objects[i].get_state())
			s_.append(np.array(goal_state[i]))


		return np.array(s_).flatten()

	def make_action(self,action):
		action = np.array(action)

		return action

	def unmake_action(self,action):
		action = list(action.reshape(self.num_cars,2))

		for i in range(len(action)):
			if action[i][1] < 0.0: 
				action[i][1] = 0.00001


		return action


	def get_train_error(self):

		avg_err = 0.0

		for i in range(len(self.X_train)):

			x = np.array([self.X_train[i]])
			y = self.Y_train[i]

			y_ = self.model.predict(x)

			err = LA.norm(y-y_)

			avg_err += err

		return avg_err/float(len(self.X_train))


	def get_cs(self,evaluations):

		count = 0.0
		avg_err = 0.0

		for rollout in evaluations:
			for datum in rollout:

				robot_action = self.make_action(datum['action'])
				sup_action = self.make_action(datum['sup_action'])
				err = LA.norm(robot_action-sup_action)

				avg_err += err
				count += 1.0


		return avg_err/count



	def get_test_error(self):

		avg_err = 0.0

		for i in range(len(self.X_test)):

			x = np.array([self.X_test[i]])
			y = self.Y_test[i]

			y_ = self.model.predict(x)

			err = LA.norm(y-y_)

			avg_err += err

		if len(self.X_test) == 0:
			return avg_err

		return avg_err/float(len(self.X_test))




	def eval_model(self,state,goal_state):

		s_ = self.make_state(state,goal_state)

		s_ = np.array([s_])
		action = self.model.predict(s_)

		return self.unmake_action(action)





