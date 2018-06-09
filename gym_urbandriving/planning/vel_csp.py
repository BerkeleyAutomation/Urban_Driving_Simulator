import constraint as csp


class VelCSP():

	def solve_csp(blob_dict):

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

		print(solutions)