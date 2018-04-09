from gym.spaces import Box 
import numpy as np



class SteeringAction:
    """
    This class is a wrapper for the action space at the lowest level of the heirarchy 
    it represents the steering and acceleration applied directly to the car. 

    """

    def __init__(self,steering =0.0, acceleration = 0.0):
        """
        Initializes the SteeringAction Class

        Parameters
        ----------
        steering: float
            the change in steering angle 
        acceleration: float
            the acceleration applied to the car
        """


        self.box = Box(low=np.array([-3,-1.0]),high=np.array([3,1.0]))
        self.controls = np.array([steering,acceleration])



    def get_value(self):
        """
        Gets the numpy array of the class

        Returns
        ----------
            steering and acceleration in numpy array shape (2,)
        """
        return self.controls

    def sample(self):
        """
        Samples a random control in this class using the OpenAI Box class

        Returns
        ----------
        steering and acceleration in numpy array shape (2,)
        """

        return self.box.sample()