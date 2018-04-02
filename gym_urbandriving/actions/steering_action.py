from gym.spaces import Box 
import numpy as np



class SteeringAction:

	def __init__(self,steering =0.0, acceleration = 0.0):


		self.box = Box(low=np.array([-30,-50.0]),high=np.array([30,50.0]))

		self.controls = np.array([steering,acceleration])

		if not self.box.contains(self.controls):
			raise Exception('Steering Controls is Out of Bounds')


	def get_value(self):
		return self.controls

	def sample():
		return self.box.sample()