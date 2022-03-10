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
_UP = 0
_DOWN = 1

_PPR = 256*16*4 # CPR * 16:1 gearbox * quadrature
_PULLEY_TEETH = 16
_BELT_PITCH = 2 # mm
_PI = 3.14159

_TICKS_PER_MM = 512
_R_MAX = 330 # mm
_TICKS_MAX = _TICKS_PER_MM * _R_MAX

# print(_TICKS_PER_MM)
MAX_LENGTH = 2

class Parser:

    def __init__(self, sp_theta1_queue, sp_theta2_queue, sp_pen_queue):
        self.th1q = sp_theta1_queue
        self.th2q = sp_theta2_queue
        self.penq = sp_pen_queue
        
        
    def read(self):
        ''' @brief   Reads data from a hpgl file.
            @details Reads each line of data and ignores input not relevant to the pen's position.
                     Takes the data points and converts them to a readable format to send to our
                     controller for setting set points for our motors.
        '''
        with open('WE_ARE_AWESOME.hpgl', 'r') as raw_hpgl:
            for line in raw_hpgl:
                split_hpgl = line.split(';')     #split the raw hpgl by the commands at the semi colons                
                # This removes all initialize, pen color, and initial pen up commands
                split_hpgl = [ ele for ele in split_hpgl if (ele != 'IN' and ele[:2] != 'SP' and ele != 'PU' and ele != ' ')]                    
                for ele in split_hpgl:
                    coords = [int(coord) for coord in ele[2:].split(',')]
                    if ele[:2] == 'PU':
                        x = coords[0] / 40
                        y = coords[1] / 40
                        th1, th2 = transform(x, y)
#                         print(x, y, th1, th2, 'up')
                        if not self.th1q.full():
                            self.th1q.put(th1)
                            self.th2q.put(th2)
                            self.penq.put(_UP)
                        last_x = x
                        last_y = y
                    elif ele[:2] == 'PD':
                        for i in range(0, len(coords), 2):
                            x = coords[i] / 40
                            y = coords[i + 1] / 40
                            interpolated = linterp2(last_x, last_y, x, y)
                            for xx, yy in interpolated:
                                th1, th2 = transform(xx, yy)
#                                 print(xx, yy, th1, th2, 'down')
                                if not self.th1q.full():
                                    self.th1q.put(th1)
                                    self.th2q.put(th2)
                                    self.penq.put(_DOWN)
                            last_x = x
                            last_y = y
                    else:
                        print(ele)
                        raise ValueError("something other than PU/PD")
        print('done parsing')
        if not self.th1q.full():
            print('last point')
            self.th1q.put(150000)
            self.th2q.put(150000)
            print('pens q')
            self.penq.put(_UP)
            print('last point queued')
        
R = 263 #mm             # Distance between the motors
x_home = 80.7
y_home = 122.676

def transform(x, y):
    '''!
    This transform calculates the two motor angles on the board given some
    point within the drawing grid.
    
    The point is calculated with respect to the corner closest to motor 1.
    This assumes the distance between the motors is R = 263mm and the "zeroed"
    length of each motor is r = 330 mm (fully extended to reach the furthest
    corners) which results in a homed location of
    (x_home, y_home) = (182.3, 122.7) mm.
    
    @param x the x coordinate
    @param y the y coordinate
    @return the motor angles (r_1, r_2) in (mm)
    '''
    # we can then calcualte the radius (mm) needed to reach any point
    # x,y (mm) on the board

    r_2 = ((y_home+y)**2 + (x_home+x)**2)**0.5
    r_1 = ((y_home+y)**2 + (R-(x_home+x))**2)**0.5
    
    th1 = int(_TICKS_PER_MM * r_1)
    th2 = int(_TICKS_PER_MM * r_2)

    return(th1, th2)

def linterp2(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    dmax = max(abs(dx), abs(dy))
    n = math.ceil(dmax / MAX_LENGTH)
    # print(n)
    points = []
    for i in range(n + 1):
        x = x1 + dx / n * i
        y = y1 + dy / n * i
        points.append((x, y))
    return points

if __name__ == '__main__':
    import task_share
    th1q = task_share.Queue('i', 1000)
    th2q = task_share.Queue('i', 1000)
    penq = task_share.Queue('i', 1000)
    
    parser = Parser(th1q, th2q, penq)
#     parser = Parser()
    parser.read()
#     print(sp_theta1_queue.get())