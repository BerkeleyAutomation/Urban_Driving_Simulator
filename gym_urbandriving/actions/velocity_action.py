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

        

        self.velocity = [velocity]


    def get_value(self):
        """
        Gets the value of the current velocity

        Returns
        ----------
            float
        """
        return self.velocity[0]
