from copy import deepcopy
import gym_urbandriving as uds
from gym_urbandriving.actions import VelocityAction
from gym_urbandriving.planning import VelCSP
import constraint as csp
import IPython
import time
import shapely

class VelocityCSPPlanner:
    def __init__(self, lookahead=10):
        self.lookahead = lookahead


    def plan(self, state, agent_num,type_of_agent = "background_cars"):

      self.state = state
      control_csp, back_csp, self.ped_csp, self.light_csp = state.get_all_future_locations()
      
      self.num_back_cars = len(back_csp)
      self.num_cont_cars = len(control_csp)
     
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


    def check_peds(self,b_1):

      for key in self.ped_csp.keys():
        if b_1[1].intersects(self.ped_csp[key]) and b_1[0].get_value() > 0:
          return False
        
      return True

    def check_light(self,b_1):

      for key in self.light_csp.keys():
        if self.light_csp[key]:
          x = self.state.dynamic_objects["traffic_lights"][key].x
          y = self.state.dynamic_objects["traffic_lights"][key].y

          box = shapely.geometry.box(x-10, y-10, x+10, y+10) #= shapely.geometry.Point((x,y)).buffer(40)
          if b_1[1].intersects(box) and b_1[0].get_value() > 0:
            return False

        
      return True



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


      for key in variables:
        problem.addConstraint(self.check_peds, [key])

      for key in variables:
        problem.addConstraint(self.check_light, [key])


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

        if cur_value >= value:
          best_solution = solution
          value = cur_value

      if best_solution == None:
        best_solution = {}
        print("NO SOLUTION")
        for i in range(self.num_back_cars):
          best_solution[str(i)+"b"] = (VelocityAction(0.0),None)
        for i in range(self.num_cont_cars):
          best_solution[str(i)+"c"] = (VelocityAction(0.0),None)

      return best_solution

