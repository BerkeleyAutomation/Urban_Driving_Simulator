from fluids.actions import SteeringAccAction
from fluids.consts import OBS_NONE
from fluids.utils import *
import pickle
import os
import time
import gzip

class DataSaver():
    """
    Saves data in numpy files organized by key. After loading from [filename]_[filenum].npy, data is in numpy array with the following data type
    np.dtype([('time', np.int32), ('obs_name', [OBS_DATA_TYPE], [OBS_SHAPE]), ..., ('act_name', np.uint8, [OBS_SHAPE])])
    Once loading the np.array, data can be accessed (for example) with data[data['key']==128] to get all data for 'key'==128
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
        self.curr_data = []
        self.dtype = None

    def generate_dtype(self):
        dtype = [('time', np.int32), ('key', np.int32)]
        k = list(self.keys)[0]
        obs, acts = self.get_obs_and_act(k)
        for obs_space, observation in obs:
            dtype.append((obs_space, observation.dtype, observation.shape))
        for act_space, action in acts:
            dtype.append((act_space, action.dtype, action.shape))
        self.dtype = np.dtype(dtype)

    def get_obs_and_act(self, key):
        observations = [] #(obs_name, observation)
        actions = [] #(act_name, action)
        for obs_space in self.obs:
            curr_observation = self.fluid_sim.state.objects[key].make_observation(obs_space).get_array() 
            observations.append((obs_space, curr_observation))
        for act_space in self.act:
            curr_act = self.fluid_sim.get_supervisor_actions(act_space, [key])[key].get_array()
            actions.append((act_space.__name__, curr_act))
        return observations, actions

    def dump(self):
        file_name = "{}_{}.npz".format(self.file, self.file_num)
        fluids_print("Dumping batch in {}".format(file_name))
        dumped_data = np.array(self.curr_data, dtype=self.dtype)
        start =  time.time()
        np.savez_compressed(file_name, dumped_data)
        fluids_print("Saved compressed file in {}s".format(round(time.time() - start)))

        self.file_num += 1
        self.curr_data = []

    def accumulate(self):
        if self.dtype == None: self.generate_dtype() # Call here to prevent state access errors if DataSaver is created before state is set.
        self.curr_batch += 1

        time = self.fluid_sim.run_time()
        for k in self.keys:
            obs, acts = self.get_obs_and_act(k)
            curr_data = np.zeros(1, dtype=self.dtype)
            curr_data['time'] = time
            curr_data['key'] = k
            for obs_space, observation in obs:
                curr_data[obs_space]= observation
            for act_space, action in acts:
                curr_data[act_space] = action
            self.curr_data.append(curr_data)
        #print("data accumulated", self.curr_batch, self.batch_size)
        if self.curr_batch % self.batch_size == 0:
            self.dump()
            self.curr_batch = 0

