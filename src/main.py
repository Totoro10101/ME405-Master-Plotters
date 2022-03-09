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
    servo1.set_angle(_UP)
    zeroed1 = False
    zeroed2 = False
    print('moving motors')
    motor1.set_duty_cycle(-70)
    motor2.set_duty_cycle(70)
    while not zeroed1 or not zeroed2:
        if lim1pin.value() == 0 and not zeroed1:
            print('m1')
            motor1.set_duty_cycle(0)
            zeroed1 = True
        if lim2pin.value() == 0 and not zeroed2:
            print('m2')
            motor2.set_duty_cycle(0)
            zeroed2 = True
        
    print('zeroed')
    
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
    print("position:", encoder1_share.get(), encoder2_share.get())
    print('controller task')
    # set the position of the encoders to the zeroing position. This must be
    # done after encoder tasks run the first time to clear accumulated ticks
    # from the zeroing process.
    encoder1.set_position(_TICKS_MAX)
    encoder2.set_position(_TICKS_MAX)
    state = _STATE_MOTOR
    curr_servo_state = 0
    servo_start_time = None
    # first setpoint
    if sp_theta1_queue.any():
        next_th1_sp = sp_theta1_queue.get()
        next_th2_sp = sp_theta2_queue.get()
        next_pen_sp = sp_pen_queue.get()
    print("first:", next_th1_sp, next_th2_sp, next_pen_sp)
    pidController.set_set_point((next_th1_sp, next_th2_sp))
    while True:
        duty1 = pidController.run(_MOTOR1)
        motor1.set_duty_cycle(duty1)
        motor2.set_duty_cycle(pidController.run(_MOTOR2))
#         print(duty1)
        if state == _STATE_MOTOR:
            move_done = pidController.check_finish_step()
#             print(move_done)
            if move_done:
#                 print("next:", next_th1_sp, next_th2_sp, next_pen_sp)
                if sp_theta1_queue.any():
                    next_pen_sp = sp_pen_queue.get()
                    next_th1_sp = sp_theta1_queue.get()
                    next_th2_sp = sp_theta2_queue.get()
                if next_pen_sp == curr_servo_state:
                    # update setpoint
                    pidController.set_set_point((next_th1_sp, next_th2_sp))
                else:
                    state = _STATE_SERVO
#                     print('servo state')
            
        elif state == _STATE_SERVO:
            _SERVO_WAIT = 500 # ms
#             print('servo state')
            if servo_start_time == None:
                servo_start_time = time.ticks_ms()
                if curr_servo_state == 0:
                    servo1.set_angle(_DOWN)
                elif curr_servo_state == 1:
                    servo1.set_angle(_UP)
            # wait cooperatively and disable controller?
            elif time.ticks_diff(time.ticks_ms(), servo_start_time) > _SERVO_WAIT:
                pidController.set_set_point((next_th1_sp, next_th2_sp))
                curr_servo_state = next_pen_sp
                servo_start_time = None
                state = _STATE_MOTOR
#                 print ('going to motor state')

        # update controller always

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
    lim2pin = pyb.Pin(pyb.Pin.cpu.C2, pyb.Pin.IN)
    lim1pin = pyb.Pin(pyb.Pin.cpu.C3, pyb.Pin.IN)
    ## \hideinitializer
    
#     LimitInt1 = pyb.ExtInt(pinC3, mode=pyb.ExtInt.IRQ_FALLING,
#                            pull=pyb.Pin.PULL_NONE, callback=onLimit1PressFCN)
#     LimitInt2 = pyb.ExtInt(pinC2, mode=pyb.ExtInt.IRQ_FALLING,
#                            pull=pyb.Pin.PULL_NONE, callback=onLimit2PressFCN) 
    
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
    startup()
    print('startup finished')
    print("position:", encoder1_share.get(), encoder2_share.get())
    parser.read()
    print('parser read')
    print(sp_theta1_queue.num_in())
    while True:
        try:
            cotask.task_list.pri_sched ()
        except KeyboardInterrupt:
            motor1.set_duty_cycle(0)
            motor2.set_duty_cycle(0)
            print('disabled')
            break