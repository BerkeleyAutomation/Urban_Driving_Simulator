import gym
from gym import error, spaces, utils
from gym.utils import seeding
import copy

class UrbanDrivingEnv(gym.Env):
  metadata = {'render.modes': ['human']}

  def __init__(self, visualizer=None, init_state=None,
               reset_random=True, reward_fn=None):
    self.visualizer = visualizer
    self.min_x, self.max_x = 0, 1000
    self.min_y, self.max_y = 0, 1000

    self.reward_fn = reward_fn

    self.init_state = init_state
    if not self.init_state:
        self.init_state = self.random_state()

    self.current_state = copy.deepcopy(self.init_state)
    self.reset_random = reset_random

  def _step(self, action, state_type="positions"):
    self.state.control_objects[0].set_action(action)

    for control_object in self.state.control_objects[1:]:
        action = control_object.eval_policy(self.current_state)
        control_object.set_action(action)
    for control_object in self.state.control_objects:
        control_object.step()

    returned_state = self.get_state_copy(state_type=state_type)
    reward = self.reward_fn(self.current_state)
    return self.get_state_copy(state_type=state_type)

  def _reset(self):
    if self.reset_random:
        self.current_state = self.random_state()
    else:
        
    return
  def _render(self, mode='human', close=False):
    if close:
        return
    self.visualizer.render(self.get_state(state_type="renderer"))

  def get_state_copy(self, state_type="positions"):
    return
