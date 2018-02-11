class PIDController:
    def __init__(self, P=1, I=0.0, D=0.0):

        self.Kp = P
        self.Ki = I
        self.Kd = D
        self.prev_error = 0
        self.integral_error = 0

    def reset(self):
        self.prev_input = 0
        self.integral_error = 0

    def get_control(self, err):
        self.integral_error += err
        derivative_error = err - self.prev_error
        self.prev_error = err

        return self.Kp*err + self.Ki*self.integral_error + self.Kd*derivative_error