from copy import deepcopy
import gym_urbandriving as uds
from gym_urbandriving.actions import VelocityAction
from gym_urbandriving.planning import VelCSP
import constraint as csp
import IPython
import time

class VelocityCSPPlanner:
    def __init__(self, lookahead=10):
        self.lookahead = lookahead


    def plan(self, state, agent_num,type_of_agent = "background_cars"):

  
      future_cs, back_cs = state.get_all_future_locations()
     
      best_solution = self.solve_csp(back_cs)

      return best_solution
  


    def solve_csp(self,blob_dict):

      ''''
      blob_dict = {'0':[[VelocityAction,blob_0],[VelocityAction,blob_1]]}
      '''
      
      problem = csp.Problem()

      for key in blob_dict.keys():
        problem.addVariables(key,blob_dict[key])

      for key_1 in blob_dict.keys():
        for key_2 in blob_dict.keys():

          if key_1 != key_2:
            problem.addConstraint(lambda b_1,b_2: not b_1[1].intersects(b_2[1]), [key_1, key_2])


      solutions = problem.getSolutions()

      best_solution = self.retrieve_velocities(solutions)
      return best_solution


    def retrieve_velocities(self,solutions):

      value = 0 
      best_solution = None
      for solution in solutions:
        cur_value = 0
        for key in solution.keys():
          cur_value += solution[key][0].get_value()

        if cur_value > value:
          best_solution = solution
          value = cur_value

      print(best_solution['0'][0].get_value())
      return best_solution

