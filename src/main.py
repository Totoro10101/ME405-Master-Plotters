"""!
@file main.py
    This file contains a program that operates a 2.5 dimensional pen plotter using a
    task based approach. 

@author             Tori Bornino
@author             Jackson McLaughlin
@author             Zach Stednitz
@date               March 15, 2022

@date   2021-Dec-15 JRR Created from the remains of previous example
@copyright (c) 2015-2021 by JR Ridgely and released under the GNU
    Public License, Version 2. 
"""

import gc
import pyb
import cotask
import task_share
import print_task
import time
import encoder
import task_startup
import task_controller
import task_parser

_PPR = 256*4*16
kp = 0.9*(360/_PPR)
ki = 0*(360/_PPR)
kd = 0*(360/_PPR)
# Read time length of step response from serial port
# _stepResponseTime = 1.5*1000  #ms
MOTOR1 = 0
MOTOR2 = 1

def task_enc1_fun():
    """!
    Task which reads encoder 1 position
    """
    while True:
        encoder1_share.put (encoder1.read())
        yield ()

def task_enc2_fun():
    """!
    Task which reads encoder 2 position
    """
    while True:
        encoder2_share.put (encoder2.read())
        yield ()
        
def task_controller_fun ():
    """!
    Task that runs a PID controller.
    """
    while True:
        if controller_state == SERVO:
            act = pidController.run(None)
            if act == True:
                controller_state == MOTOR:
            else:
                servo.set_pwm()
            
        
        if controller_state == MOTOR:
            duty1 = pidController.run(MOTOR1)
            duty2 = pidController.run(MOTOR2)
        
            if duty1 == False or duty2 == False 
                motor1.set_duty_cycle(0)
                motor2.set_duty_cycle(0)
                controller_state = SERVO
            else:
                motor1.set_duty_cycle(duty1)
                motor2.set_duty_cycle(duty2)
            
        yield ()
        
# def task_data1_fun ():
#     done = False
#     while True:
#         if time.ticks_diff(time.ticks_ms(), tasks_start_time) < _stepResponseTime:
#             print_task.put(pidController1.get_data_str())
#         else:
#             if not done:
#                 print_task.put("Done!\n")
#                 done = True
#         yield ()

# This code creates a share for each encoder object, creates encoder objects to read from, creates controller
# objects and sets the gain and set point positions. 
if __name__ == "__main__":

    # Create 2 encoder shares to share position data.
    encoder1_share = task_share.Share('i', thread_protect = False, name = "Encoder 1 Share")
    encoder2_share = task_share.Share('i', thread_protect = False, name = "Encoder 2 Share")
    
    # Create a Queue with set points (theta_1, theta_2, Pen_up/down) (ticks)
    set_point_queue = task_share.Queue()
    
    
    
    # Instantiate encoders with default pins and timer
    encoder1 = encoder.EncoderDriver(pyb.Pin.cpu.B6, pyb.Pin.cpu.B7, 4)
    encoder2 = encoder.EncoderDriver(pyb.Pin.cpu.C6, pyb.Pin.cpu.C7, 8)
    
    # Instantiate proportional controllers with initial gains and  
    pidController = task_controller.PIDController(set_point_Queue, 1, 0, 0,
                                                  encoder1_share, encoder2_share)
    pidController.set_gains(kp, ki, kd)
    
      
    # Instantiate motors with default pins and timer
    motor1 = motor.MotorDriver(pyb.Pin.board.PA10, pyb.Pin.board.PB4,
                               pyb.Pin.board.PB5, pyb.Timer(3, freq=20000))
    motor2 = motor.MotorDriver(pyb.Pin.board.PC1, pyb.Pin.board.PA0,
                               pyb.Pin.board.PA1, pyb.Timer(5, freq=20000))
    
    
    # Instantiate servo
    
    
    
    
    

    # Create the tasks. If trace is enabled for any task, memory will be
    # allocated for state transition tracing, and the application will run out
    # of memory after a while and quit. Therefore, use tracing only for 
    # debugging and set trace to False when it's not needed
    task_encoder1 = cotask.Task (task_enc1_fun, name = 'Encoder_1_Task', priority = 2, 
                         period = 10, profile = True, trace = False)
    task_encoder2 = cotask.Task (task_enc2_fun, name = 'Encoder_2_Task', priority = 2, 
                         period = 10, profile = True, trace = False)
    task_controller = cotask.Task (task_controller_fun, name = 'Controller_Task', priority = 1, 
                         period = 300, profile = True, trace = False)
    
#     task_data1 = cotask.Task (task_data1_fun, name = 'Data Collection Task', priority = 0,
#                               period = 10, profile = True, trace = False)
    
    cotask.task_list.append (task_encoder1)
    cotask.task_list.append (task_encoder2)
    cotask.task_list.append (task_controller)

#     cotask.task_list.append (task_data1)

    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect ()

    # Run the scheduler with the chosen scheduling algorithm. Quit if KeyboardInterrupt
    tasks_start_time = time.ticks_ms()
    while True:
        try:
            cotask.task_list.pri_sched ()
        except KeyboardInterrupt:
            break