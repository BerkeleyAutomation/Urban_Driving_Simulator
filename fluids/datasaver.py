from fluids.actions import SteeringAccAction
from fluids.consts import OBS_NONE
from fluids.utils import *
import pickle
import os

class DataSaver():
    """
    Saves data in pickle file. After loading from pickle, data is in following format
    dict[time]["obs"][OBS_NAME][key]
    dict[time]["act"][ACT_NAME][key]
    """

    def __init__(self, fluid_sim, file, keys=None, obs=[OBS_NONE], act=[SteeringAccAction], batch_size=500, make_dir=True):
        """
            Save data from FLUIDS simulation.

            fluid_sim (required): FluidSim data that is being saved
            file (required): Filename with path to dump data to. Multiple files 
                             with suffixes _1, _2 etc. might be created if data
                             gets too large
            keys: Keys of cars to gather observations from. Default is controlled car keys.
            obs: List of observations to record. Default is [OBS_NONE]
            act: List of actions to record. Default is [SteeringAccAction]
            batch_size: Number of iterations to run before dumping data. Default is 500.
            make_dir: Boolean. Flags if directory specified should be created or not.
        """
        self.fluid_sim = fluid_sim
        self.file = file
        self.obs = obs
        self.act = act
        self.batch_size = batch_size
        self.keys = keys
        if self.keys == None:
            self.keys = self.fluid_sim.state.background_cars.keys()
        if make_dir:
            dir = os.path.dirname(self.file)
            os.makedirs(dir, exist_ok=True)

        self.curr_batch = 0
        self.file_num = 0
        self.curr_data = {}
        self.separator = "_"

    def dump(self):
        file_name = "{}{}{}{}".format(self.file, self.separator, self.file_num, ".pickle")
        fluids_print("Dumping batch in {}".format(file_name))


        with open(file_name, 'wb') as handle:
            pickle.dump(self.curr_data, handle, protocol=pickle.HIGHEST_PROTOCOL)
        self.curr_data = {}
        self.file_num += 1

    def accumulate(self):
        self.curr_batch += 1

        time = self.fluid_sim.run_time()
        observations = {}
        for obs_space in self.obs:
            curr_observation = {k:self.fluid_sim.state.objects[k].make_observation(obs_space).get_array() for k in self.keys} # TODO: add **obs_args
            observations[obs_space] = curr_observation

        actions = {}
        for act_space in self.act:
            curr_act = self.fluid_sim.get_supervisor_actions(act_space, self.keys)
            actions[act_space.__name__] = curr_act
        
        curr_data = {
                "obs": observations,
                "act": actions
                }
        self.curr_data[time] = curr_data
        #print("data accumulated", self.curr_batch, self.batch_size)
        if self.curr_batch % self.batch_size == 0:
            self.dump()
            self.curr_batch = 0

