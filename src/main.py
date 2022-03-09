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

# import task_parser
import encoder
import motor
import servo
import task_controller
import test_parser
# import print_task


_PPR = 256*4*16

kp = 3.6*(360/_PPR)
ki = 0*(360/_PPR)
kd = 0*(360/_PPR)

_TICKS_PER_MM = 512
_R_MAX = 330 # mm
_TICKS_MAX = _TICKS_PER_MM * _R_MAX

# Read time length of step response from serial port
# _stepResponseTime = 1.5*1000  #ms

# Motor IDs
_MOTOR1 = 0
_MOTOR2 = 1


# Servo pwm values
##  @brief The servo pwm location to move to when the pen is up
_UP = 8
##  @brief The servo pwm location to move to when the pen is down
_DOWN = 7

_STATE_MOTOR = 0
_STATE_SERVO = 1

def startup():
    '''!
    This method will initialize the pen plotter.
    
    This process includes running the motors until the limit switches are
    triggered. 
    '''
#     print('pen up')
    servo1.set_angle(_UP)
    
#     m = 1
#     n=1
#     o =1
#     zeroed = [False, False]
#     limit1_share.put(0)
#     limit2_share.put(0)
#     print('moving motors')
#     motor1.set_duty_cycle(-70)
#     motor2.set_duty_cycle(70)
#     print(not zeroed[0] or not zeroed[1])
#     while not zeroed[0] or not zeroed[1]:
#         if limit1_share.get() == 1 and not zeroed[0]:
#             print('m1')
#             motor1.set_duty_cycle(0)
#             zeroed[0] = True
#         if limit2_share.get() == 1 and not zeroed[1]:
#             print('m2')
#             motor2.set_duty_cycle(0)
#             zeroed[1] = True
#     while limit1_share.get() == 0 or limit2_share.get() == 0:
#         if o==1:
#             print('while')
#             o=2
# #         print(limit1_share.get(), limit2_share.get())
#         if limit1_share.get():
#             if m==1:
#                 print('motor1')
#                 m=2
#             # stop motors while moving pen
#             # one is negative because one rotates clockwise positive and the
#             # rotates clockwise negative
#             motor1.set_duty_cycle(0)
#         if limit2_share.get():
#             if n==1:
#                 print('motor2')
#                 n=2
#             # stop motors while moving pen
#             # one is negative because one rotates clockwise positive and the
#             # rotates clockwise negative
#             motor2.set_duty_cycle(0)
        
        
    print('zeroed')
    encoder1.set_position(_TICKS_MAX)
    encoder2.set_position(_TICKS_MAX)
    

def onLimit1PressFCN(IRQ_src):
    '''!@brief       Sets buttonFlag True when button is pushed.
       @details     Used as the callback function for the interrupt.
                    Records that the button was pressed.
       @param       IRQ_src Source of the interrupt. Required by MicroPython
                            for callback functions, but unused.
    '''
    limit1_share.put(1)
    LimitInt1.disable()
    
def onLimit2PressFCN(IRQ_src):
    '''!@brief       Sets buttonFlag True when button is pushed.
       @details     Used as the callback function for the interrupt.
                    Records that the button was pressed.
       @param       IRQ_src Source of the interrupt. Required by MicroPython
                            for callback functions, but unused.
    '''
    limit2_share.put(1)
    LimitInt2.disable()

def task_enc1_fun():
    """!
    Task which reads encoder 1 position
    """
    while True:
        value = encoder1.read()
        encoder1_share.put(value)
#         print(value, end=' ')
        yield ()

def task_enc2_fun():
    """!
    Task which reads encoder 2 position
    """
    while True:
        value = encoder2.read()
        encoder2_share.put(value)
#         print(value)
        yield ()
        
def task_controller_fun ():
    """!
    Task that runs a PID controller.
    """
    print('controller task')
    state = _STATE_SERVO
    curr_servo_state = 0
    # first setpoint
    curr_theta1_sp = sp_theta1_queue.get()
    curr_theta2_sp = sp_theta2_queue.get()
    curr_pen_sp = sp_pen_queue.get()
    print("first", curr_theta1_sp, curr_theta2_sp, curr_pen_sp)
    pidController.set_set_point((curr_theta1_sp, curr_theta2_sp))
    servo_start_time = None
    
    servo1.set_angle(_UP)
    print('setting angle')
    while True:
        if state == _STATE_MOTOR:
            pen_change = curr_pen_sp != curr_servo_state
#             print(pen_change, end=' ')
            move_done = pidController.check_finish_step()
#             print(move_done)
            if pen_change and move_done: # pen needs to move and motor move is done
                state = _STATE_SERVO
#                 print('changing to servo state')
            elif not pen_change and move_done:
                # next setpoint
                curr_theta1_sp = sp_theta1_queue.get()
                curr_theta2_sp = sp_theta2_queue.get()
                curr_pen_sp = sp_pen_queue.get()
                print("updated", curr_theta1_sp, curr_theta2_sp, curr_pen_sp)
                pidController.set_set_point((curr_theta1_sp, curr_theta2_sp))
                
        elif state == _STATE_SERVO:
            _SERVO_WAIT = 500 # ms
#             print('servo state')
            if servo_start_time == None:
                servo_start_time = time.ticks_ms()
                if curr_servo_state == 0:
                    servo1.set_angle(_DOWN)
                    curr_servo_state = curr_pen_sp
                elif curr_servo_state == 1:
                    servo1.set_angle(_UP)
            # wait cooperatively and disable controller?
            elif time.ticks_diff(time.ticks_ms(), servo_start_time) > _SERVO_WAIT:
                curr_servo_state = curr_pen_sp
                servo_start_time = None
                state = _STATE_MOTOR
#                 print ('going to motor state')
        # update controller always
        duty1 = pidController.run(_MOTOR1)
        motor1.set_duty_cycle(duty1)
        motor2.set_duty_cycle(pidController.run(_MOTOR2))
#         print(duty1)
        yield ()
        
# This code creates a share for each encoder object, creates encoder objects to read from, creates controller
# objects and sets the gain and set point positions. 

if __name__ == "__main__":


    # Create 2 limit switch shares to share limit switch condition.
    limit1_share = task_share.Share('i', thread_protect = False, name = "Limit 1 Share")
    limit2_share = task_share.Share('i', thread_protect = False, name = "Limit 2 Share")
    
    # Create 2 encoder shares to share position data.
    encoder1_share = task_share.Share('i', thread_protect = False, name = "Encoder 1 Share")
    encoder2_share = task_share.Share('i', thread_protect = False, name = "Encoder 2 Share")
    
    # Create a Queue with set points (theta_1, theta_2, Pen_up/down) (ticks)
    sp_theta1_queue = task_share.Queue('i', 1000)
    sp_theta2_queue = task_share.Queue('i', 1000)
    sp_pen_queue = task_share.Queue('i', 1000)
    
    parser = test_parser.Parser(sp_theta1_queue, sp_theta2_queue, sp_pen_queue)
    
    # Instantiate encoders with default pins and timer
    encoder1 = encoder.EncoderDriver(pyb.Pin.cpu.B6, pyb.Pin.cpu.B7, 4)
    encoder2 = encoder.EncoderDriver(pyb.Pin.cpu.C6, pyb.Pin.cpu.C7, 8)
    
    # Instantiate limit switches
    pinC2 = pyb.Pin(pyb.Pin.cpu.C2)
    pinC3 = pyb.Pin(pyb.Pin.cpu.C3)
    ## \hideinitializer
    LimitInt1 = pyb.ExtInt(pinC3, mode=pyb.ExtInt.IRQ_FALLING,
                           pull=pyb.Pin.PULL_NONE, callback=onLimit1PressFCN)
    LimitInt2 = pyb.ExtInt(pinC2, mode=pyb.ExtInt.IRQ_FALLING,
                           pull=pyb.Pin.PULL_NONE, callback=onLimit2PressFCN) 
    
    # Instantiate servo
    servo1 = servo.Servo(pin1 = pyb.Pin.board.PA9,
                         timer = pyb.Timer(1, freq=50), timerChannel = 2)
    
    # Instantiate motors with default pins and timer
    motor2 = motor.MotorDriver(pyb.Pin.board.PA10, pyb.Pin.board.PB4,
                               pyb.Pin.board.PB5, pyb.Timer(3, freq=20000))
    motor1 = motor.MotorDriver(pyb.Pin.board.PC1, pyb.Pin.board.PA0,
                               pyb.Pin.board.PA1, pyb.Timer(5, freq=20000))
    
    # Instantiate proportional controllers with initial gains  
    pidController = task_controller.PIDController(1, 0, 0, (_TICKS_MAX, _TICKS_MAX),
                                                  encoder1_share, encoder2_share)
    pidController.set_gains(kp, ki, kd)

    # Create the tasks. If trace is enabled for any task, memory will be
    # allocated for state transition tracing, and the application will run out
    # of memory after a while and quit. Therefore, use tracing only for 
    # debugging and set trace to False when it's not needed


    task_encoder1 = cotask.Task (task_enc1_fun, name = 'Encoder_1_Task', priority = 3, 
                         period = 10, profile = True, trace = False)
    task_encoder2 = cotask.Task (task_enc2_fun, name = 'Encoder_2_Task', priority = 3, 
                         period = 10, profile = True, trace = False)
    task_controller = cotask.Task (task_controller_fun, name = 'Controller_Task', priority = 1, 
                         period = 10, profile = True, trace = False)
    
    cotask.task_list.append (task_encoder1)
    cotask.task_list.append (task_encoder2)
    cotask.task_list.append (task_controller)

    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect ()

    # Run the scheduler with the chosen scheduling algorithm. Quit if KeyboardInterrupt
#     tasks_start_time = time.ticks_ms()
    limit1_share.put(0)
    limit2_share.put(0)
    startup()
    print('startup finished')
    
    parser.read()
    print('parser read')
    while True:
        try:
            cotask.task_list.pri_sched ()
        except KeyboardInterrupt:
            motor1.set_duty_cycle(0)
            motor2.set_duty_cycle(0)
            print('disabled')
            break