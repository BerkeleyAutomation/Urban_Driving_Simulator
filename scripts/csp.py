
import constraint as csp
problem = csp.Problem()
problem.addVariables(["a","b"], [1, 2, 3])
problem.addConstraint(lambda a, b: b == a+1, ["a", "b"])
solutions = problem.getSolutions()

print(solutions)