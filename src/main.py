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
import task_startup
import task_encoder
import task_controller
import task_parser

_PPR = 256*4*16
kp = 0.9*(360/_PPR)
ki = 0*(360/_PPR)
kd = 0*(360/_PPR)
# Read time length of step response from serial port
# _stepResponseTime = 1.5*1000  #ms

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
        
def task_controller1_fun ():
    """!
    Task that runs a PID controller.
    """
    while True:
        motor1.set_duty_cycle(pidController1.run()) # set motor duty
        yield ()
        
def task_data1_fun ():
    done = False
    while True:
        if time.ticks_diff(time.ticks_ms(), tasks_start_time) < _stepResponseTime:
            print_task.put(pidController1.get_data_str())
        else:
            if not done:
                print_task.put("Done!\n")
                done = True
        yield ()

def task_controller2_fun ():
    """!
    Task that runs a PID controller.
    """
    while True:
        motor2.set_duty_cycle(pidController2.run()) # set motor duty
        yield ()

# def task_data2_fun ():
#     done = False
#     while True:
#         if time.ticks_diff(time.ticks_ms(), tasks_start_time) < _stepResponseTime:
#             print_task.put(pidController2.get_data_str())
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
    
    # Instantiate encoders with default pins and timer
    encoder1 = encoder.EncoderDriver(pyb.Pin.cpu.B6, pyb.Pin.cpu.B7, 4)
    encoder2 = encoder.EncoderDriver(pyb.Pin.cpu.C6, pyb.Pin.cpu.C7, 8)
    
    # Instantiate proportional controllers with initial gains and  
    pidController1 = pidcontroller.PIDController(0, 1, 0, 0, encoder1_share)
    pidController2 = pidcontroller.PIDController(0, 1, 0, 0, encoder2_share)
    
    pidController1.set_gains(kp, ki, kd)
    pidController2.set_gains(kp, ki, kd)
    # Read desired set point position from serial port
    # Converts degrees to ticks
    pidController1.set_set_point(float(360)*(_PPR/360))
    pidController2.set_set_point(float(360)*(_PPR/360))
    
    # Instantiate motor 1 with default pins and timer
    motor1 = motor.MotorDriver(pyb.Pin.board.PA10, pyb.Pin.board.PB4,
                               pyb.Pin.board.PB5, pyb.Timer(3, freq=20000))
    motor2 = motor.MotorDriver(pyb.Pin.board.PC1, pyb.Pin.board.PA0,
                               pyb.Pin.board.PA1, pyb.Timer(5, freq=20000))

    # Create the tasks. If trace is enabled for any task, memory will be
    # allocated for state transition tracing, and the application will run out
    # of memory after a while and quit. Therefore, use tracing only for 
    # debugging and set trace to False when it's not needed
    task_encoder1 = cotask.Task (task_enc1_fun, name = 'Encoder_1_Task', priority = 2, 
                         period = 10, profile = True, trace = False)
    task_encoder2 = cotask.Task (task_enc2_fun, name = 'Encoder_2_Task', priority = 2, 
                         period = 10, profile = True, trace = False)
    task_controller1 = cotask.Task (task_controller1_fun, name = 'Controller_1_Task', priority = 1, 
                         period = 300, profile = True, trace = False)
    task_controller2 = cotask.Task (task_controller2_fun, name = 'Controller_2_Task', priority = 1, 
                         period = 300, profile = True, trace = False)
    task_data1 = cotask.Task (task_data1_fun, name = 'Data Collection Task', priority = 0,
                              period = 10, profile = True, trace = False)
    
    cotask.task_list.append (task_encoder1)
    cotask.task_list.append (task_controller1)
    cotask.task_list.append (task_encoder2)
    cotask.task_list.append (task_controller2)
    cotask.task_list.append (task_data1)

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