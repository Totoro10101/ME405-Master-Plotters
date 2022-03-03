'''!@file       encoder.py
    A driver for reading from Quadrature Encoders. Includes the class Encoder.
    
    @author     Tori Bornino
    @author     Jackson McLaughlin
    @author     Zach Stednitz
    @date       January 13, 2022
'''

import pyb

##  @brief      Encoder overflow period.
#   @details    The Encoder AR value 2**16-1.
_ENC_PERIOD = 2 ** 16 - 1 # Ticks overflow period for the encoder

class EncoderDriver:
    '''!Interface with quadrature encoders. This class is a driver for
        quadrature encoders. It uses the timer functions of the nucleo board.
        It provides functions for getting position while being safe from
        overflow or underflow errors, and allows for the zeroing of position
        of the encoder.
    '''
    
    def __init__(self, pin1, pin2, timerID, timerChannel1=1, timerChannel2=2):
        '''!Constructs an encoder object. The Encoder object stores position
            and delta values and provides methods to get position or delta and
            to set position. The hardware timer is set up in this constructor.
            
            @param      pin1            First encoder pin
            @param      pin2            Second encoder pin
            @param      timerID         Timer ID number of timer to use
            @param      timerChannel1   Channel 1 id number. Default 1
            @param      timerChannel2   Channel 2 id number. Default 2
        '''
        self._timer = pyb.Timer(timerID,period=(_ENC_PERIOD),prescaler=0)
        # Channels are never called in code, but they enable the timer counter 
        self._channel_1 = self._timer.channel(timerChannel1,
                                              mode=pyb.Timer.ENC_AB,pin=pin1)
        self._channel_2 = self._timer.channel(timerChannel2,
                                              mode=pyb.Timer.ENC_AB,pin=pin2)

        ##  @brief     Calculated position of the encoder
        #   @details   Most recent calculated position of the motor shaft
        #              in ticks.
        self.position = 0
        
        ##  @brief     Current encoder reading 
        #   @details   Current encoder reading in ticks stored to calculate 
        #              change in position between readings.
        self.currentTick = 0
        
    def read(self):
        '''!Updates and returns encoder position. Updates variables which store
            position values. Compensates for overflow and underflow.
            
            @return     The position of the encoder shaft in ticks                    
        '''
        # Calculate the change in position in ticks using the last
        # measured value
        lastTick = self.currentTick
        self.currentTick = self._timer.counter()
        delta = self.currentTick - lastTick
        
        # Compensate for overflow.
        if delta >= _ENC_PERIOD / 2:
            delta -= _ENC_PERIOD
        elif delta <= -_ENC_PERIOD / 2:
            delta += _ENC_PERIOD
        
        # Record the current position for next iteration delta calculation
        self.position += delta
        
        return self.position
    
    def zero(self):
        '''!Sets encoder position to zero. Sets the encoder position in ticks
            to zero.
        '''
        self.position = 0
        
if __name__ == '__main__':
    
    import time
    
    # Instantiate encoder 1 with default pins and timer
    enc1 = Encoder(pyb.Pin.cpu.B6, pyb.Pin.cpu.B7, 4)
    
    # Print the encoder read position in ticks every 0.5 seconds
    try:
        print('The encoder position in ticks is:')
        while True:
            print(enc1.read())
            time.sleep(.5)
            
    except KeyboardInterrupt:
        print('Done reading encoder position')
