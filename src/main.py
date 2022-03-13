"""!
@file main.py
    This file contains a program that operates a 2.5 dimensional pen
    plotter using a task based a_PPRoach. 

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

import encoder
import motor
import servo
import controller
import task_parser

# Encoder pulses (ticks) per revolution
_PPR = 256*4*16

# Gains for motor PID controller (using P only)
_KP = 4*(360/_PPR)
_KI = 0*(360/_PPR)
_KD = 0*(360/_PPR)

## @brief Encoder ticks per mm of belt length change.
#  @details There are 512 ticks/mm because there are 16 teeth on the drive
#           pulleys, at 2mm pitch, for 32mm of belt length per revolution.
#           Dividing the _PPR of the encoder by 32mm gives 512 ticks/mm. 
TICKS_PER_MM = 512
## @brief Maximum length of either belt.
R_MAX = 330 # mm
## @brief Maximum position of either motor (ticks)
TICKS_MAX = TICKS_PER_MM * R_MAX

# Motor IDs
_MOTOR1 = 0
_MOTOR2 = 1

##  @brief The servo pwm to set when the pen is up (% duty cycle)
UP = 8
##  @brief The servo pwm to set when the pen is down (% duty cycle)
DOWN = 7

def startup():
    '''!
    This method will initialize the pen plotter.
    
    This process includes running the motors until the limit switches are
    triggered. The pen will be up during this routine.
    '''
    servo1.set_angle(UP)
    zeroed1 = False
    zeroed2 = False
    print('moving motors')
    motor1.set_duty_cycle(-70)
    motor2.set_duty_cycle(70)
    while not zeroed1 or not zeroed2:
        if limit1_pin.value() == 0 and not zeroed1:
            print('m1')
            motor1.set_duty_cycle(0)
            zeroed1 = True
        if limit2_pin.value() == 0 and not zeroed2:
            print('m2')
            motor2.set_duty_cycle(0)
            zeroed2 = True
    print('startup finished')
    
def task_enc1_fun():
    """!
    Task which reads encoder 1 position
    """
    while True:
        value = encoder1.read()
        encoder1_share.put(value)
        yield ()

def task_enc2_fun():
    """!
    Task which reads encoder 2 position
    """
    while True:
        value = encoder2.read()
        encoder2_share.put(value)
        yield ()
        
def task_controller_fun ():
    """!
    Task that runs a PID controller that controls both motors and the servo.
    """
    # States of controller FSM
    _STATE_MOTOR = 0
    _STATE_SERVO = 1
    
    # Set the position of the encoders to the zeroing position. This must be
    # done after encoder tasks run the first time to clear accumulated ticks
    # from the zeroing process.
    encoder1.set_position(TICKS_MAX)
    encoder2.set_position(TICKS_MAX)
    
    # Initial state: Motor is controlled and pen is up from startup
    state = _STATE_MOTOR
    curr_servo_state = 0
    servo_start_time = None
    
    # Load the first setpoint
    if sp_theta1_queue.any():
        next_th1_sp = sp_theta1_queue.get()
        next_th2_sp = sp_theta2_queue.get()
        next_pen_sp = sp_pen_queue.get()
#     print("first:", next_th1_sp, next_th2_sp, next_pen_sp)
    pidController.set_set_point((next_th1_sp, next_th2_sp))
    
    
    while True:
        # Always update the controller first
        motor1.set_duty_cycle(pidController.run(_MOTOR1))
        motor2.set_duty_cycle(pidController.run(_MOTOR2))
        
        if state == _STATE_MOTOR:
            move_done = pidController.check_finish_step()
            if move_done:
                # Retrieve the next setpoint in the queue, but don't update
                # the controller yet (pen may need to move)
                if sp_theta1_queue.any():
                    next_pen_sp = sp_pen_queue.get()
                    next_th1_sp = sp_theta1_queue.get()
                    next_th2_sp = sp_theta2_queue.get()
                if next_pen_sp == curr_servo_state:
                    # Update controller if pen is already in position
                    pidController.set_set_point((next_th1_sp, next_th2_sp))
                else:
                    # If pen position needs to change, go to servo state
                    state = _STATE_SERVO
            
        elif state == _STATE_SERVO:
            # Time that the servo needs to change position
            _SERVO_WAIT = 500 # ms
            if servo_start_time == None:
                servo_start_time = time.ticks_ms()
                if curr_servo_state == 0:
                    servo1.set_angle(DOWN)
                elif curr_servo_state == 1:
                    servo1.set_angle(UP)
            # Wait for servo
            elif time.ticks_diff(time.ticks_ms(),
                                 servo_start_time) > _SERVO_WAIT:
                pidController.set_set_point((next_th1_sp, next_th2_sp))
                curr_servo_state = next_pen_sp
                servo_start_time = None
                state = _STATE_MOTOR
        yield ()
        
if __name__ == "__main__":
    # Create 2 limit switch shares to share limit switch condition.
    # 1 is unpressed, 0 is pressed (active-low configuration).
    limit1_share = task_share.Share('i', thread_protect=False,
                                    name="Limit 1 Share")
    limit2_share = task_share.Share('i', thread_protect = False,
                                    name = "Limit 2 Share")
    
    # Create 2 encoder shares to share position data.
    encoder1_share = task_share.Share('i', thread_protect = False,
                                      name = "Encoder 1 Share")
    encoder2_share = task_share.Share('i', thread_protect = False,
                                      name = "Encoder 2 Share")

    # Create Queues with set points (theta_1, theta_2, Pen_up/down) (ticks).
    sp_theta1_queue = task_share.Queue('i', 2000)
    sp_theta2_queue = task_share.Queue('i', 2000)
    sp_pen_queue = task_share.Queue('i', 2000)
    
    # Create the HPGL parser.
    parser = task_parser.Parser(sp_theta1_queue, sp_theta2_queue, sp_pen_queue)
    
    # Instantiate encoders with default pins and timer.
    encoder1 = encoder.EncoderDriver(pyb.Pin.cpu.B6, pyb.Pin.cpu.B7, 4)
    encoder2 = encoder.EncoderDriver(pyb.Pin.cpu.C6, pyb.Pin.cpu.C7, 8)
    
    # Instantiate limit switches
    limit2_pin = pyb.Pin(pyb.Pin.cpu.C2, pyb.Pin.IN)
    limit1_pin = pyb.Pin(pyb.Pin.cpu.C3, pyb.Pin.IN)
    
    # Instantiate servo
    servo1 = servo.Servo(pin1 = pyb.Pin.board.PA9,
                         timer = pyb.Timer(1, freq=50), channel = 2)
    
    # Instantiate motors with default pins and timer
    motor1 = motor.MotorDriver(pyb.Pin.board.PC1, pyb.Pin.board.PA0,
                               pyb.Pin.board.PA1, pyb.Timer(5, freq=20000))
    motor2 = motor.MotorDriver(pyb.Pin.board.PA10, pyb.Pin.board.PB4,
                            pyb.Pin.board.PB5, pyb.Timer(3, freq=20000))
    
    # Instantiate proportional controller with initial gains and setpoint
    pidController = controller.PIDController(1, 0, 0, (TICKS_MAX, TICKS_MAX),
                                             encoder1_share, encoder2_share)
    pidController.set_gains(_KP, _KI, _KD)

    # Create the tasks. If trace is enabled for any task, memory will be
    # allocated for state transition tracing, and the application will run out
    # of memory after a while and quit. Therefore, use tracing only for 
    # debugging and set trace to False when it's not needed.
    task_encoder1 = cotask.Task(task_enc1_fun, name='Encoder_1_Task',
        priority=3, period=10, profile=True, trace=False)
    task_encoder2 = cotask.Task(task_enc2_fun, name = 'Encoder_2_Task',
        priority=3, period=10, profile=True, trace=False)
    task_controller = cotask.Task(task_controller_fun, name='Controller_Task',
        priority=1, period=10, profile=True, trace=False)
    
    cotask.task_list.append(task_encoder1)
    cotask.task_list.append(task_encoder2)
    cotask.task_list.append(task_controller)

    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect()

    # Run the startup routine to home the encoders 
    startup()
    # parse the selected HPGL file
    parser.read('WE_ARE_AWESOME.hpgl')
    
    # Run the scheduler with the chosen scheduling algorithm.
    # Quit if KeyboardInterrupt.
    while True:
        try:
            cotask.task_list.pri_sched()
        except KeyboardInterrupt:
            motor1.set_duty_cycle(0)
            motor2.set_duty_cycle(0)
            print('disabled')
            break