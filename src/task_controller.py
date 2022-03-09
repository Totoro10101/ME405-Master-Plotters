'''!@file task_controller.py
    A class that performs closed loop PID control.
    
    @author     Tori Bornino
    @author     Jackson McLaughlin
    @author     Zach Stednitz
    @date       March 15, 2022
'''

import time

# Set Point variable locations
_MOTOR1 = 0
_MOTOR2 = 1



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
        
        # Proportional actiation value
        Pduty = -self._Kp*self._error[motorID]
        
        # Integral actuation value
        _Iduty_new = self._Ki*self._error[motorID]*(curr_time - self._last_time[motorID])
        if (self._Iduty[motorID] > 0 and _Iduty_new < 0) \
            or  (self._Iduty[motorID] < 0 and _Iduty_new > 0):
            self._Iduty[motorID] = _Iduty_new
        else:
            self._Iduty[motorID] += _Iduty_new
        
        # Differential actuation value
        Dduty = self._Kd*(self._error[motorID]-self._last_error[motorID])/(curr_time - self._last_time[motorID])
        
        # PID actuation value
        actuation_value = Pduty + self._Iduty[motorID] + Dduty
        
        
        # Filter saturated values
        if actuation_value > 100:
            actuation_value = 100
        elif actuation_value < -100:
            actuation_value = -100
        
        # Store values for next iteration
        self._last_error[motorID] = self._error[motorID]
        self._last_time[motorID] = curr_time
                           
            
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
        if abs(self._error[_MOTOR1]) < 100 and abs(self._error[_MOTOR2]) < 100:
            self._step_start_time = [None, None]
            self._error = [0, 0]
            done = True
        return done

                   
















# '''!@file task_controller.py
#     A class that performs closed loop PID control.
#     
#     @author     Tori Bornino
#     @author     Jackson McLaughlin
#     @author     Zach Stednitz
#     @date       March 15, 2022
# '''
# 
# import time
# 
# # State Variables
# _STATE_SERVO = 0
# _STATE_MOTOR = 1
# 
# # Servo run variables
# ##  @brief wait time for servo to reach set point before continuing to draw
# SERVO_WAIT = 1000 # ms
# 
# 
# # Set Point Queue variable locations
# _MOTOR1 = 0
# _MOTOR2 = 1
# _SERVO = 2
# 
# _MOTORS = [_MOTOR1, _MOTOR2]
# 
# # Servo Setpoints
# _UP = False
# _DOWN = True
# 
# # Servo pwm values
# ##  @brief The servo pwm location to move to when the pen is up
# MOVE_UP = 8
# ##  @brief The servo pwm location to move to when the pen is down
# MOVE_DOWN = 7
# 
# 
# 
# class PIDController:
#     '''! 
#     This class implements a PID controller to run a pen plotter.
#     It contains methods for calculating the actuation value 
#     and setting the Kp, Ki, and Kd gains. 
#     ''' 
#     
#     def __init__ (self, Kp, Ki, Kd, set_point_queue, sensor_share1, sensor_share2):
#         '''! 
#         Creates a PID controller by initializing controller gains and storing
#         the queue of setpoints and (2) shares with sensor data. 
#         
#         @param Kp               The proportional gain for the controller.
#                                 Units of (dutyCycle/ticks)
#         @param Ki               The integral gain for the controller.
#                                 Units of (dutyCycle/(ticks*seconds))
#         @param Kd               The derivative gain for the controller.
#                                 Units of (dutyCycle/(ticks/seconds))
#         @param set_point_queue  A queue containing the desired set point
#                                 locations of the step response.  
#         @param sensor_share1    A share that contains the read position from
#                                 sensor 1 in a (2) sensor system with
#                                 independently controlled actuators.
#         @param sensor_share2    A share that contains the read position from
#                                 sensor 2 in a (2) sensor system with
#                                 independently controlled actuators.
#         '''
#         
#         self._set_point_queue = set_point_queue
#         self._Kp = Kp
#         self._Ki = Ki
#         self._Kd = Kd
#         self._sensor_share = [sensor_share1, sensor_share2]
# 
#         ##  @brief  Current controller state (servo / motor).
#         self.state = _STATE_MOTOR
#         ##  @brief  Current state of the servo (up false / down true).
#         self.curr_servo_state = _UP
#         
#         ##  @brief      Tuple with current set point. Where the motor set points
#         #               are in ticks and the pen position is a boolean.
#         #               (theta_1, theta_2, Pen)
#         self.curr_set_point = (None, None, None)
#         
#         # Step response start time for each motor
#         self._step_start_time = [None, None]
#         # Step response start time for the servo
#         self._servo_start_time = None
#         
#         # Store data to calculate actuation values
#         self._error = [0, 0]
#         self._last_time = [0, 0]
#         self._last_error = [0, 0]
#         self._Iduty = [0, 0]
#         
# #         ##  @brief Data Collection Start Time
# #         self.data_start_time = [None, None]
#         
# 
#         
#         
#     def run(self):
#         '''! 
#         Continuously runs the control algorithm. Reads the position data from a
#         sensor and then finds the error between the actual position and the 
#         desired set point value. When the setpoint value is reached, the next
#         set point is read from the queue. When the pen state (up/down) changes,
#         the motors stop until the servo reaches the desired state/
#         
#         @return The actuation value to fix steady state error. When in the servo
#                 state, the actuation value is the servo pwm. If the actuation
#                 value is True, then the state changes to motor. When in the
#                 motor state, then actuation value is a tuple for motors (1, 2)
#                 of the duty cycle. If the actuation value is False,
#                 then the state changes to servo.
#         '''
#         # There are two states, the servo and the motor. When the servo reaches
#         # its position, the state changes to the motors. When both motors reach
#         # their setpoint, the next set of setpoints are loaded. If the pen state
#         # changes, then the state changes back to the servo, if the pen state
#         # does not change then the state remains at motor.
#         
#         
#         # in this state, the servo is controlled
#         if self.state == _STATE_SERVO:
#                         
#             # First, store the servo step start time
#             if self._servo_start_time == None:
#                 self._servo_start_time = time.ticks_ms()
#             
#             # then toggle the servo setpoint to up or down. The servo pwm
#             # locations are defined above.
#             if self.curr_set_point[_SERVO] == _UP:
#                 actuation_value = MOVE_UP
#                 self.curr_servo_state = _UP
#             elif self.curr_set_point[_SERVO] == _DOWN:
#                 actuation_value = MOVE_DOWN 
#                 self.curr_servo_state = _DOWN
#             
#             # after the set servo step time the state changes to motor 
#             if time.ticks_diff(time.ticks_ms, self._servo_start_time) >= SERVO_WAIT:
#                 self._servo_start_time = None
#                 self.state = _STATE_MOTOR
#                 actuation_value = True
#                 
#                 
#         # In this state, the motors are controlled.    
#         elif self.state == _STATE_MOTOR:
#                                  
#             # Check if current set point has been reached, if it has, then the
#             # setpoint is changed to the new point
#             if abs(self._error[_MOTOR1]) < 100 and abs(self._error[_MOTOR2]) < 100:
#                 self.curr_set_point = self._set_point_queue.get()
#                 self._step_start_time = [None, None]
#                 self._error = [0, 0]
#                 
#                 # if in the new set point the pen position changes, then the
#                 # state changes to servo to toggle the pen location.
#                 if self.curr_servo_state != self.curr_set_point[_SERVO]:
#                     self.state = _STATE_SERVO
#                     actuation_value = False
#                     
#             # If the current set point has not been reached, then the actuation
#             # value is calculated for each motor.
#             else: 
#                 
#                 for motorID in _MOTORS: 
#                     # Store initial motor step time
#                     if self._step_start_time[motorID] == None:
#                         self._step_start_time[motorID] = time.ticks_ms()
#                         self._last_time[motorID] = self._step_start_time[motorID]
#                     
#                     # Calculate the current error in position
#                     self._error[motorID] = self._sensor_share[motorID].get() - self.curr_set_point[motorID]
#                     curr_time = time.ticks_diff(time.ticks_ms(),self._step_start_time[motorID])
#                     
#                     
#                     # Calculate the PID actuation value
#                     
#                     # Proportional actiation value
#                     Pduty = -self._Kp*self._error[motorID]
#                     
#                     # Integral actuation value
#                     _Iduty_new = self._Ki*self._error[motorID]*(curr_time - self._last_time[motorID])
#                     if (self._Iduty[motorID] > 0 and _Iduty_new < 0) \
#                         or  (self._Iduty[motorID] < 0 and _Iduty_new > 0):
#                         self._Iduty[motorID] = _Iduty_new
#                     else:
#                         self._Iduty[motorID] += _Iduty_new
#                     
#                     # Differential actuation value
#                     Dduty = self._Kd*(self._error[motorID]-self._last_error[motorID])/(curr_time - self._last_time[motorID])
#                     
#                     # PID actuation value
#                     actuation_value[motorID] = Pduty + self._Iduty[motorID] + Dduty
#                     
#                     
#                     # Filter saturated values
#                     if actuation_value[motorID] > 100:
#                         actuation_value[motorID] = 100
#                     elif actuation_value[motorID] < -100:
#                         actuation_value[motorID] = -100
#                     
#                     # Store values for next iteration
#                     self._last_error[motorID] = self._error[motorID]
#                     self._last_time[motorID] = curr_time
#                            
#             
#         return actuation_value
# 
# 
#     def set_gains(self, Kp, Ki, Kd):
#         '''! 
#         Sets the proportional gain controller value.
#         
#         @param Kp           The proportional gain for the controller.
#                             Units of (dutyCycle/ticks)
#         @param Ki           The integral gain for the controller.
#                             Units of (dutyCycle/(ticks*seconds))
#         @param Kd           The derivative gain for the controller.
#                             Units of (dutyCycle/(ticks/seconds))
#         '''
#         self._Kp = Kp
#         self._Ki = Ki
#         self._Kd = Kd
#         
#         
#         
# #     def set_set_point(self, set_point):
# #         '''! 
# #         Sets the desired setpoint for the step response.
# #         
# #         @param set_point  The desired steady state response value.  
# #         '''
# #         self._set_point = set_point
#         
# 
#                    
# #     def get_data_str(self):
# #         '''!
# #         Returns the current time (ms) and position (ticks) as a string.
# #         The string output is: "time,position\r\n"
# #         '''
# #         if self.data_start_time == None:
# #             self.data_start_time = time.ticks_ms()
# #         return f"{time.ticks_diff(time.ticks_ms(),self.data_start_time)},{self._sensor_share.get()}\n"
# 
# 
# 
# 