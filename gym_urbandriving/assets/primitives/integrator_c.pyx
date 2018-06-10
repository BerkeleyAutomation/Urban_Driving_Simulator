import sys
cimport numpy as np

#import some often used math functions from the c math library
cdef extern from "math.h":
    double sin(double)

cdef extern from "math.h":
    double cos(double)

cdef extern from "math.h":
    double atan(double)

cdef extern from "math.h":
      double tan(double)


 
class Model:
    """
    This class can be used to integrate a differential equation
    """
    def __init__(self,float acc,float delta_f,float l_r,float l_f):
      """
      -a is the amplitude of the sine function that describes the 
      speed oscillation as a function time
      -p controls the period of the sine function
      """
      self.acc=acc
      self.delta_f=delta_f
      self.l_r = l_r
      self.l_f = l_f
     
    def __call__(self,np.ndarray[np.float64_t, ndim=1] state,float t):
      """
      y is the current state of the initial value problem:
      y: position
      t: time
      """
      x, y, vel, rad_angle = state

      # Differential equations
      beta = atan((self.l_r / (self.l_f + self.l_r)) * tan(self.delta_f))
      dx = vel * cos(rad_angle + beta)
      dy = vel * -sin(rad_angle + beta)
      dangle = (vel / self.l_r) * sin(beta)
      dvel = self.acc
      output = [dx, dy, dvel, dangle]
      return output