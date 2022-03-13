'''!@file task_controller.py
    A class that performs closed loop PID control.
    
    @author     Tori Bornino
    @author     Jackson McLaughlin
    @author     Zach Stednitz
    @date       March 15, 2022
'''

import time

# Motor IDs
_MOTOR1 = 0
_MOTOR2 = 1

## @brief Maximum allowable power to set on the motors (percent duty cycle).
MAX_POWER = 100

class PIDController:
    '''! 
    This class implements a PID controller to run a pen plotter.
    It contains methods for calculating the actuation value 
    and setting the Kp, Ki, and Kd gains. 
    ''' 
    
    def __init__ (self, Kp, Ki, Kd, set_point, sensor_share1, sensor_share2):
        '''! 
        Creates a PID controller by initializing controller gains and storing
        the queue of setpoints and (2) shares with sensor data. 
        
        @param Kp               The proportional gain for the controller.
                                Units of (dutyCycle/ticks)
        @param Ki               The integral gain for the controller.
                                Units of (dutyCycle/(ticks*seconds))
        @param Kd               The derivative gain for the controller.
                                Units of (dutyCycle/(ticks/seconds))
        @param set_point        The initial setpoint value.  
        @param sensor_share1    A share that contains the read position from
                                sensor 1 in a (2) sensor system with
                                independently controlled actuators.
        @param sensor_share2    A share that contains the read position from
                                sensor 2 in a (2) sensor system with
                                independently controlled actuators.
        '''
        self._set_point = set_point
        self._Kp = Kp
        self._Ki = Ki
        self._Kd = Kd
        self._sensor_share = [sensor_share1, sensor_share2]

        # Step response start time for each motor
        self._step_start_time = [None, None]

        # Store data to calculate actuation values
        self._error = [0, 0]
        self._last_time = [0, 0]
        self._last_error = [0, 0]
        self._Iduty = [0, 0]

    def run(self, motorID):
        '''! 
        Runs the control algorithm. Reads the position data from a
        sensor and then finds the error between the actual position and the 
        desired set point value. Then calculates the setpoint value.
        
        @param  The motor that you are controlling.
        @return The actuation value to fix steady state error. When in the servo
                state, the actuation value is the servo pwm. If the actuation
                value is True, then the state changes to motor. When in the
                motor state, then actuation value is a tuple for motors (1, 2)
                of the duty cycle. If the actuation value is False,
                then the state changes to servo.
        '''
        # Store initial motor step time
        if self._step_start_time[motorID] == None:
            self._step_start_time[motorID] = time.ticks_ms()
            self._last_time[motorID] = self._step_start_time[motorID]
        
        # Calculate the current error in position
        self._error[motorID] = self._sensor_share[motorID].get() - self._set_point[motorID]
        curr_time = time.ticks_diff(time.ticks_ms(),self._step_start_time[motorID])
        
        # Calculate the PID actuation value
        # Proportional component of actuation value
        Pduty = -self._Kp*self._error[motorID]
        
        # Integral component of actuation value
        _Iduty_new = self._Ki*self._error[motorID]*(curr_time - self._last_time[motorID])
        if (self._Iduty[motorID] > 0 and _Iduty_new < 0) \
            or  (self._Iduty[motorID] < 0 and _Iduty_new > 0):
            self._Iduty[motorID] = _Iduty_new
        else:
            self._Iduty[motorID] += _Iduty_new
        
        # Differential component of actuation value
        Dduty = self._Kd*(self._error[motorID]-self._last_error[motorID])/(curr_time - self._last_time[motorID])
        
        # Total PID actuation value
        actuation_value = Pduty + self._Iduty[motorID] + Dduty

        # Filter saturated values
        if actuation_value > MAX_POWER:
            actuation_value = MAX_POWER
        elif actuation_value < -MAX_POWER:
            actuation_value = -MAX_POWER

        # Store values for next iteration
        self._last_error[motorID] = self._error[motorID]
        self._last_time[motorID] = curr_time

        # Compensate for swapped directions on each motor due to belt
        if motorID == _MOTOR1:
            return -actuation_value
        elif motorID == _MOTOR2:
            return actuation_value

    def set_gains(self, Kp, Ki, Kd):
        '''! 
        Sets the proportional gain controller value.
        
        @param Kp           The proportional gain for the controller.
                            Units of (dutyCycle/ticks)
        @param Ki           The integral gain for the controller.
                            Units of (dutyCycle/(ticks*seconds))
        @param Kd           The derivative gain for the controller.
                            Units of (dutyCycle/(ticks/seconds))
        '''
        self._Kp = Kp
        self._Ki = Ki
        self._Kd = Kd
        
    def set_set_point(self, set_point):
        '''! 
        Sets the desired setpoint for the step response.
        
        @param set_point  The desired steady state response value. It is in the
                          form of a tuple (theta_1, theta_2, pen) in ticks.
        '''
        self._set_point = set_point
        
        # Step response start time for each motor
        self._step_start_time = [None, None]
        
        # Store data to calculate actuation values
        self._error = [0, 0]
        self._last_time = [0, 0]
        self._last_error = [0, 0]
        self._Iduty = [0, 0]
        
    def check_finish_step(self):
        '''!
        Check if current set point has been reached by both motors.
        
        @return a boolean is returned for if the setpoint has been reached.
        '''
        done = False
#         print(self._error[_MOTOR1], self._error[_MOTOR2])
        if abs(self._error[_MOTOR1]) < 1000 and abs(self._error[_MOTOR2]) < 1000:
            self._step_start_time = [None, None]
            self._error = [0, 0]
            done = True
        return done
