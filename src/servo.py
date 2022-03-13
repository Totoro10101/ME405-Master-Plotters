'''!@file servo.py
    A class that controls the servo.
    
    @author     Tori Bornino
    @author     Jackson McLaughlin
    @author     Zach Stednitz
    @date       March 15, 2022
'''

import pyb

class Servo:
    """!
    This class contains methods to control the angle of a servo.
    """
    def __init__(self, pin1=pyb.Pin.board.PA9, timer=pyb.Timer(1, freq=50),
                 channel=2):
        """!
        This instantiates a servo object.
        
        @param pin1     The servo signal pin, default pyb.Pin.board.PA9
        @param timer    The servo tmer, default pyb.Timer(1, freq=50)
        @param channel  The timer channel ID, default 2
        """   
        self._pin1 = pyb.Pin(pin1, pyb.Pin.OUT_PP)
        self._timer = timer
        self._channel = self._timer.channel(channel, pyb.Timer.PWM, pin=pin1)
        
        
    def set_angle(self, angle):
        """!
        This method sets the servo angle.
        
        Valid range is between 2-13 with the center at 7.5 
        """
        self._channel.pulse_width_percent(angle)
        
# Test program for servos
if __name__ == "__main__":
    import time
    servo1 = Servo()
    time.sleep(1)
    print('moving')
    servo1.set_angle(7)
    time.sleep(3)
    servo1.set_angle(8)
    time.sleep(0.5)
    print('moved')