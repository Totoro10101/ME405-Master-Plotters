'''!@file motor.py
    A driver for controlling a motor driver board using PWM.
    
    @author     Tori Bornino
    @author     Jackson McLaughlin
    @author     Zach Stednitz
    @date       January 13, 2022
'''
import pyb
class MotorDriver:
    '''! 
    This class implements a motor driver for an ME405 kit. 
    '''
    def __init__ (self, en_pin, in1pin, in2pin, timer):
        '''! 
        Creates a motor driver by initializing GPIO
        pins and turning the motor off for safety. 
        @param en_pin   The pin on the Nucleo connected to the enable pin
                        on the motor driver.
        @param in1pin   The pin on the nucleo connected to the first input pin
                        on the motor driver.
        @param in2pin   The pin on the nucleo connected to the second input pin
                        on the motor driver.
        @param timer    The timer object to use to control PWM.
        '''
        self._en_pin = pyb.Pin(en_pin, pyb.Pin.OUT_PP)
        self._timer = timer
        
        self._ch1 = self._timer.channel(1, pyb.Timer.PWM, pin=in1pin)
        self._ch2 = self._timer.channel(2, pyb.Timer.PWM, pin=in2pin)

    def set_duty_cycle (self, level):
        '''!
        This method sets the duty cycle to be sent
        to the motor to the given level. Positive values
        cause torque in one direction, negative values
        in the opposite direction.
        @param level A signed integer holding the duty
               cycle of the voltage sent to the motor 
        '''
        if level < 0 and level >= -100:
            ch1_level = 0
            ch2_level = -level
        elif level == 0:
            ch1_level = 0
            ch2_level = 0
        elif level > 0 and level <= 100:
            ch1_level = level
            ch2_level = 0
        else:
            raise ValueError("level must be between -100 and 100")
        self._en_pin.high()
        self._ch1.pulse_width_percent(ch1_level)
        self._ch2.pulse_width_percent(ch2_level)

# Test program for motors
if __name__ == "__main__":
    import time
    _ena_pin = pyb.Pin.board.PA10
    _in1a_pin = pyb.Pin.board.PB4
    _in2a_pin = pyb.Pin.board.PB5
    _tim3 = pyb.Timer(3, freq=20000)
    _moe1 = MotorDriver(_ena_pin, _in1a_pin, _in2a_pin, _tim3)
    
    _ena_pin2 = pyb.Pin.board.PC1
    _in1a_pin2 = pyb.Pin.board.PA0
    _in2a_pin2 = pyb.Pin.board.PA1
    _tim32 = pyb.Timer(5, freq=20000)
    _moe2 = MotorDriver(_ena_pin2, _in1a_pin2, _in2a_pin2, _tim32)
    
    print('moving')
    _moe1.set_duty_cycle(0)
    _moe2.set_duty_cycle(70)
    time.sleep(2)
    _moe1.set_duty_cycle(0)
    _moe2.set_duty_cycle(0)
    print('done')