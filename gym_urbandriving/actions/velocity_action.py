from gym.spaces import Box 
import numpy as np



class VelocityAction:

	def __init__(self,velocity_float=0.0):

		self.box = Box(low=0.0,high=5.0,shape=(1,))

		self.velocity = np.array([velocity_float])

		if not self.box.contains(self.velocity):
			raise Exception('Velocity is Out of Bounds')


	def get_value(self):
		return self.velocity[0]

	def sample():
		return self.box.sample()