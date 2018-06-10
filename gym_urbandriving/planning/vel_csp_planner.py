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

  
      control_csp, back_csp = state.get_all_future_locations()
     
      best_solution = self.solve_csp(back_csp,control_csp)


      control_solution, back_solution = self.decompose_solution(best_solution)


      state.solve_for_velocity = False
      state.control_velocity = control_solution
      state.background_velocity = back_solution


      return best_solution
  

    def decompose_solution(self,best_solution):

      control_solution = {}
      background_solution = {}

      for key in best_solution.keys():

        if key[-1] == "b":
          background_solution[key[0:-1]] = best_solution[key]
        elif key[-1] == "c":
          control_solution[key[0:-1]] = best_solution[key]
      return control_solution,background_solution

    def solve_csp(self,background_dict,control_dict):

      ''''
      blob_dict = {'0':[[VelocityAction,blob_0],[VelocityAction,blob_1]]}
      '''
      
      problem = csp.Problem()
      variables = []

      for key in background_dict.keys():
        var_name = key+"b"
        problem.addVariable(var_name,background_dict[key])
        variables.append(var_name)

      for key in control_dict.keys():
        var_name = key+"c"
        problem.addVariable(var_name,control_dict[key])
        variables.append(var_name)


      for key_1 in variables:
        for key_2 in variables:
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

      return best_solution

