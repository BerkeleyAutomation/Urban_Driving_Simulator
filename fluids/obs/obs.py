class FluidsObs(object):
    """
    The base FLUIDS observation interface
    """
    def __init__(self):
        pass
    def get_array(self):
        """
        Returns a numpy array representation of the observation

        Returns
        -------
        np.array
        """
        raise NotImplementedError
