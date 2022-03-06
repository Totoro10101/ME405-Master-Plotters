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
import pyb
import time
import gc

import task_share
import cotask

import task_startup
import task_parser
import encoder
import motor
import servo
import task_controller
# import print_task


_PPR = 256*4*16

kp = 0.9*(360/_PPR)
ki = 0*(360/_PPR)
kd = 0*(360/_PPR)

# Read time length of step response from serial port
# _stepResponseTime = 1.5*1000  #ms

# Motor IDs
_MOTOR1 = 0
_MOTOR2 = 1

# Controller states
_SERVO = 0
_MOTOR = 1


def onLimit1PressFCN(IRQ_src):
    '''@brief       Sets buttonFlag True when button is pushed.
       @details     Used as the callback function for the interrupt.
                    Records that the button was pressed.
       @param       IRQ_src Source of the interrupt. Required by MicroPython
                            for callback functions, but unused.
    '''
    limit1_share.put(True)
    
def onLimit2PressFCN(IRQ_src):
    '''@brief       Sets buttonFlag True when button is pushed.
       @details     Used as the callback function for the interrupt.
                    Records that the button was pressed.
       @param       IRQ_src Source of the interrupt. Required by MicroPython
                            for callback functions, but unused.
    '''
    limit2_share.put(True)


# def task_parser_fun():
#     """
#     Task which converts HPGL code describing the drawing to setpoints for the
#     controller.
#     """

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
        controller_state = _MOTOR
        
        if controller_state == _SERVO:
            act = pidController.run()
            if act == True:
                controller_state == _MOTOR:
            else:
                try:
                    servo.set_angle(act)
                except ValueError:
                    print("Servo Value Error: {:}".format(act))
        
        elif controller_state == _MOTOR:
            duty = pidController.run()      
            if duty == False  
                motor1.set_duty_cycle(0)
                motor2.set_duty_cycle(0)
                controller_state = _SERVO
            else:
                try:
                    motor1.set_duty_cycle(duty[_MOTOR1])
                    motor2.set_duty_cycle(duty[_MOTOR2])
                except ValueError:
                    print("Servo Value Error: {:}".format(duty))
                    
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


    # Create 2 limit switch shares to share limit switch condition.
    limit1_share = task_share.Share('b', thread_protect = False, name = "Limit 1 Share")
    limit2_share = task_share.Share('b', thread_protect = False, name = "Limit 2 Share")
    
    # Create 2 encoder shares to share position data.
    encoder1_share = task_share.Share('i', thread_protect = False, name = "Encoder 1 Share")
    encoder2_share = task_share.Share('i', thread_protect = False, name = "Encoder 2 Share")
    
    # Create a Queue with set points (theta_1, theta_2, Pen_up/down) (ticks)
    set_point_queue = task_share.Queue()
    
    
    # Instantiate encoders with default pins and timer
    encoder1 = encoder.EncoderDriver(pyb.Pin.cpu.B6, pyb.Pin.cpu.B7, 4)
    encoder2 = encoder.EncoderDriver(pyb.Pin.cpu.C6, pyb.Pin.cpu.C7, 8)
    
    # Instantiate limit switches
    pinC2 = pyb.Pin(pyb.Pin.cpu.C2)
    pinC3 = pyb.Pin(pyb.Pin.cpu.C3)
    ## \hideinitializer
    LimitInt1 = pyb.ExtInt(pinC2, mode=pyb.ExtInt.IRQ_RISING,
                           pull=pyb.Pin.PULL_UP, callback=onLimit1PressFCN)
    LimitInt2 = pyb.ExtInt(pinC3, mode=pyb.ExtInt.IRQ_RISING,
                           pull=pyb.Pin.PULL_UP, callback=onLimit2PressFCN) 
    
    # Instantiate servo
    servo1 = servo.Servo(pin1 = pyb.Pin.board.PA6,
                         timer = pyb.Timer(3, freq=50), timerChannel = 1)
    
    # Instantiate motors with default pins and timer
    motor1 = motor.MotorDriver(pyb.Pin.board.PA10, pyb.Pin.board.PB4,
                               pyb.Pin.board.PB5, pyb.Timer(3, freq=20000))
    motor2 = motor.MotorDriver(pyb.Pin.board.PC1, pyb.Pin.board.PA0,
                               pyb.Pin.board.PA1, pyb.Timer(5, freq=20000))
    
    
    
    # Instantiate parser task
    
    
    # Instantiate proportional controllers with initial gains  
    pidController = task_controller.PIDController(set_point_Queue, 1, 0, 0,
                                                  encoder1_share, encoder2_share)
    pidController.set_gains(kp, ki, kd)
    
    
        
    

    # Create the tasks. If trace is enabled for any task, memory will be
    # allocated for state transition tracing, and the application will run out
    # of memory after a while and quit. Therefore, use tracing only for 
    # debugging and set trace to False when it's not needed


#     task_parser = cotask.Task (task_parser_fun, name = 'Parser_Task', priority = 2, 
#                          period = 100, profile = True, trace = False)
    task_encoder1 = cotask.Task (task_enc1_fun, name = 'Encoder_1_Task', priority = 3, 
                         period = 10, profile = True, trace = False)
    task_encoder2 = cotask.Task (task_enc2_fun, name = 'Encoder_2_Task', priority = 3, 
                         period = 10, profile = True, trace = False)
    task_controller = cotask.Task (task_controller_fun, name = 'Controller_Task', priority = 1, 
                         period = 300, profile = True, trace = False)
    
#     task_data1 = cotask.Task (task_data1_fun, name = 'Data Collection Task', priority = 0,
#                               period = 10, profile = True, trace = False)



    # Zero the plotter at startup:
    limit1_share.put(False)
    limit2_share.put(False)
    
    
    
    
    
    
    
#     cotask.task_list.append (task_parser)
    cotask.task_list.append (task_encoder1)
    cotask.task_list.append (task_encoder2)
    cotask.task_list.append (task_controller)

#     cotask.task_list.append (task_data1)

    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect ()

    # Run the scheduler with the chosen scheduling algorithm. Quit if KeyboardInterrupt
#     tasks_start_time = time.ticks_ms()
    
    while True:
        try:
            # run startupscript before scheduler?
            cotask.task_list.pri_sched ()
        except KeyboardInterrupt:
            break