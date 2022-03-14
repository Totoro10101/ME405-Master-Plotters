"""!
@file task_parser.py
    This file contains a program that parses an HPGL file and then turns it
    into a format that contains the location of x and y and pen commands.

@author             Tori Bornino
@author             Jackson McLaughlin
@author             Zach Stednitz
@date               March 15, 2022

"""
# import task_share
import math

# Pen States
_UP = 0
_DOWN = 1

## @brief   Encoder pulses (ticks) per revolution
#  @details The encoder pulses or ticks per revolution of the pulley is 256
#           counts per revolution times 4 pulses per count for a quadrature
#           encoder time 16 for the 16:1 ratio between the backshaft of the
#           motor where the encoder is and the output shaft of the gearbox
#           where the pulley is.
PPR = 256*4*16

## @brief   Dots per mm from the Inkscape HPGL output.
#  @details By default, Inkscape outputs HPGL files with units of 1/40th of a
#           millimeter, since this is the [resolution of the HP plotters]
#           (https://en.wikipedia.org/wiki/HP-GL)
#           which HPGL was originally designed for.
DPMM = 40

##  @brief Conversion from R (mm) to theta (ticks).
#   This value is developed in the [Kinematic  Derivation] @ref page_kinematics
#   page.
TICKS_PER_MM = 512

##  @brief Zeroed length of pen plotter arms.
#   Measured from the pen center to the motor center.
#   Assumed that both motor 1 and motor 2 radii are the same 
R_MAX = 330 # mm

# The following constants are used for the transform calculation
## @brief   Center distance between the motors (mm).
#  @details Used for the transform from (x, y) coordinates to motor angles.
R = 263             
## @brief   Position of the drawing origin with respect to the motors origin.
#  @details x-coordinate of the top left corner of the drawing area with
#           respect to the left motor (mm).
#           Used for the transform from (x, y) coordinates to motor angles.
X_HOME = 80.7
## @brief   Position of the drawing origin with respect to the motors origin.
#  @details y-coordinate of the top left corner of the drawing area with
#           respect to the left motor (mm).
#           Used for the transform from (x, y) coordinates to motor angles.
Y_HOME = 122.676

## @brief   Maximum length (mm) between two consecutive points.
#  @details Used for interpolation to smooth the drawing profile.
MAX_LENGTH = 2

class Parser:
    '''!
    This class will parse an HPGL file and output a set of points 
    (theta_1, theta_2, pen) stored in three separate queues.
    
    The method includes interpolation that will split up long lines into
    smaller lines to smooth drawing. The derivation of the kinematics that
    drive the translation from desired location in (x, y) [mm] to motor angles
    (theta_1, theta_2) [ticks] is explainied in the [Kinematic  Derivation]
    @ref page_kinematics page.
    '''
    
    def __init__(self, sp_theta1_queue, sp_theta2_queue, sp_pen_queue):
        '''!
        This class computes the set of points (theta_1, theta_2, pen)
        and stores them in three separate queues.
        
        @param sp_theta1_queue  A queue for the setpoint motor angle, theta_1.
        @param sp_theta2_queue  A queue for the setpoint motor angle, theta_2.
        @param sp_pen_queue     A queue for the pen condition for the movement
                                to the desired pen location (theta_1, theta_2).
        '''
        self._th1q = sp_theta1_queue
        self._th2q = sp_theta2_queue
        self._penq = sp_pen_queue
        
        
    def read(self, hpgl_file):
        '''!
        Reads data from an hpgl file and converts it to desired set points
        (theta_1, theta_2, pen).
        
        Reads each line of data and ignores inputs not relevant to the pen's
        position. Takes the data points and converts them to a readable format
        to send via a queue to our controller for setting set points for our
        motors.
        
        @param hpgl__file the name of the hpgl file you want parsed.
        '''
        print("parsing hpgl...")
        
        with open(hpgl_file, 'r') as raw_hpgl:
            # This section of the code reads the hpgl file, then splits it up
            # into the proper coordinates (x, y, pen). Any non-relevant
            # information is ignored.
            for line in raw_hpgl:
                # split the raw hpgl by the commands at the semi colons. HPGL
                # usually comes in one line of all commands.
                split_hpgl = line.split(';')                      
                # This removes all non-relevant commands such as:
                # initialize, pen color, and initial pen up commands
                split_hpgl = [ ele for ele in split_hpgl \
                               if (ele != 'IN' and ele[:2] != 'SP' \
                                   and ele != 'PU' and ele != ' ')]                    
                # This takes each command (pen up PU or pen down PD) and splits
                # the command into the individual pen coordinates while adding
                # the state of the pen as a third component of the coordinate.
                for ele in split_hpgl:
                    # split command into pairs of coordinates (x,y)
                    coords = [int(coord) for coord in ele[2:].split(',')]
                    # add the pen condition to the stored coordinate (x,y,pen)
                    # then transform to (theta_1, theta_2, pen)
                    
                    # PU exclusively comes with one coordinate 
                    if ele[:2] == 'PU':
                        x = coords[0] / DPMM
                        y = coords[1] / DPMM
                        
                        th1, th2 = transform(x, y)
                        if not self._th1q.full():
                            self._th1q.put(th1)
                            self._th2q.put(th2)
                            self._penq.put(_UP)
                        last_x = x
                        last_y = y
                    
                    # PD generally comes with multiple coordinates. When two
                    # consecutive coordinates are more than _MAX_LENGTH away
                    # from each other, they are split up into smaller line
                    # segments where each is less than our equal to . 
                    elif ele[:2] == 'PD':
                        for i in range(0, len(coords), 2):
                            x = coords[i] / DPMM
                            y = coords[i + 1] / DPMM
                            
                            interpolated = linterp2(last_x, last_y, x, y)
                            for xx, yy in interpolated:
                                th1, th2 = transform(xx, yy)
                                if not self._th1q.full():
                                    self._th1q.put(th1)
                                    self._th2q.put(th2)
                                    self._penq.put(_DOWN)
                            last_x = x
                            last_y = y
                    
                    # check for command value errors 
                    else:
                        print(ele)
                        raise ValueError("something other than PU/PD")
              
        # Add the command to go to the home position after drawing the image.
        # This makes it easier to see the picture drawn.
        if not self._th1q.full():
            self._th1q.put(150000)
            self._th2q.put(150000)
            self._penq.put(_UP)
            
        print('done parsing')
 
def transform(x, y):
    '''!
    This transform calculates the two motor angles on the board given some
    point within the drawing grid.
    
    The point is calculated with respect to the corner closest to motor 1.
    This assumes the distance between the motors is _R = 263mm and the "zeroed"
    length of each motor is r = 330 mm (fully extended to reach the furthest
    corners) which results in a homed location of
    (_x_home, _y_home) = (182.3, 122.7) mm.
    
    @param x the x coordinate (mm)
    @param y the y coordinate (mm)
    @return the motor angles (r_1, r_2) in (ticks)
    '''
    # we can then calcualte the radius (mm) needed to reach any point
    # x,y (mm) on the board

    r_2 = ((Y_HOME + y)**2 + (X_HOME + x)**2)**0.5
    r_1 = ((Y_HOME + y)**2 + (R - (X_HOME + x))**2)**0.5
    
    th1 = int(TICKS_PER_MM * r_1)
    th2 = int(TICKS_PER_MM * r_2)

    return(th1, th2)


def linterp2(x1, y1, x2, y2):
    '''!
    This method divides a line into smaller segments.
    
    @param x1 The starting x value of the line
    @param y1 The starting y value of the line
    @param x2 The ending x value of the line
    @param y2 The ending y value of the line
    @return the list of interpolated points (x,y) defining the smaller segments
    '''
    dx = x2 - x1
    dy = y2 - y1
    dmax = max(abs(dx), abs(dy))
    n = math.ceil(dmax / MAX_LENGTH)
    points = []
    for i in range(n + 1):
        x = x1 + dx / n * i
        y = y1 + dy / n * i
        points.append((x, y))
        
    return points


# When run as main, this will parse the inputed HPGL file.
if __name__ == '__main__':
    
    import task_share
    
    _th1q = task_share.Queue('i', 1000)
    _th2q = task_share.Queue('i', 1000)
    _penq = task_share.Queue('i', 1000)
    
    parser = Parser(_th1q, _th2q, _penq)
    parser.read('WE_ARE_AWESOME.hpgl')