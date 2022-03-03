'''!@file task_controller.py
    A class that performs closed loop PID control.
    
    @author     Tori Bornino
    @author     Jackson McLaughlin
    @author     Zach Stednitz
    @date       March 15, 2022
'''

import time
import motor

class PIDController:
    '''! 
    This class implements a PID controller. It contains methods for setting the
    set point, Kp, Ki, and Kd gains. As well as a method for printing run data:
    time (ms) and position (ticks).
    '''
   
    def __init__ (self, set_point, Kp, Ki, Kd, sensor_share1, sensor_share2):
        '''! 
        Creates a proportional controller by initializing setpoints and gains
        
        @param setpoint      The initial desired location of the step response  
        @param Kp            The proportional gain for the controller.
                             Units of (dutyCycle/ticks)
        @param Ki            The integral gain for the controller.
                             Units of (dutyCycle/(ticks*seconds))
        @param Kd            The derivative gain for the controller.
                             Units of (dutyCycle/(ticks/seconds))
        @param sensor_share  A share the contains the read position from sensor        
        '''
        
        self._set_point = set_point
        self._Kp = Kp
        self._Ki = Ki
        self._Kd = Kd
        self._sensor_share = [sensor_share1, sensor_share2]
        
        
        ##  @brief      Step response start time
        self.step_start_time = [None, None]
        
        # Store data to calculate actuation value
        self._last_time = [0, 0]
        self._last_error = [0, 0]
        self._Iduty = [0, 0]
        
        ##  @brief Data Collection Start Time
        self.data_start_time = [None, None]
        
        
    def run(self, motorID):
        '''! 
        Continuously runs the control algorithm. Reads the position data from a
        sensor and then finds the error between the actual position and the 
        desired setpoint value. Then we append the stored data list with a
        tuple of values.
        
        @return The actuation value to fix steady state error.
        '''
        # Store initial step time
        if self.step_start_time[motorID] == None:
            self.step_start_time[motorID] = time.ticks_ms()
            self._last_time[motorID] = self.step_start_time[motorID]
        
        # Calculate the current error in position
        error = self._sensor_share[motorID].get() - self._set_point[motorID]
        curr_time = time.ticks_diff(time.ticks_ms(),self.step_start_time[motorID])
        
        # Calculate the PID actuation value
        Pduty = -self._Kp*error
        
        _Iduty_new = self._Ki*error*(curr_time - self._last_time[motorID])
        if (self._Iduty[motorID] > 0 and _Iduty_new < 0) \
            or  (self._Iduty[motorID] < 0 and _Iduty_new > 0):
            self._Iduty[motorID] = _Iduty_new
        else:
            self._Iduty[motorID] += _Iduty_new
        
        Dduty = self._Kd*(error-self._last_error[motorID])/(curr_time - self._last_time[motorID])
        
        actuation_value = Pduty + self._Iduty[motorID] + Dduty
                
        # Filter saturated values
        if actuation_value > 100:
            actuation_value = 100
        elif actuation_value < -100:
            actuation_value = -100
        
        # Store values for next iteration
        self._last_error[motorID] = error
        self._last_time[motorID] = curr_time
        
        return actuation_value
    
    def set_set_point(self, set_point):
        '''! 
        Sets the desired setpoint for the step response.
        
        @param set_point  The desired steady state response value.  
        '''
        self._set_point = set_point
        
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
                   
    def get_data_str(self):
        '''!
        Returns the current time (ms) and position (ticks) as a string.
        The string output is: "time,position\r\n"
        '''
        if self.data_start_time == None:
            self.data_start_time = time.ticks_ms()
        return f"{time.ticks_diff(time.ticks_ms(),self.data_start_time)},{self._sensor_share.get()}\n"