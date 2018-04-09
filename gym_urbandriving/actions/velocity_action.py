from gym.spaces import Box 
import numpy as np



class VelocityAction:
    """
    This class is a wrapper for the velocity control in the hierarchy
    it represents the target velocity for the car to drive at
    """

    def __init__(self,velocity=0.0):
        """
        Initializes the VelocityAction Class

        Parameters
        ----------
        velocity: float
            the desired velocity 
        """

        self.box = Box(low=0.0,high=5.0,shape=(1,))

        self.velocity = np.array([velocity])

        if not self.box.contains(self.velocity):
            raise Exception('Velocity is Out of Bounds')


    def get_value(self):
        """
        Gets the value of the current velocity

        Returns
        ----------
            float
        """
        return self.velocity[0]

    def sample(self):
        """
        Samples a random control in this class using the OpenAI Box class

        Returns
        ----------
        velocity in numpy array shape (1,)
        """
        return self.box.sample()