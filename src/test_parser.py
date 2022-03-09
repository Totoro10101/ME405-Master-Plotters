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

_UP = 0
_DOWN = 1

_PPR = 256*16*4 # CPR * 16:1 gearbox * quadrature
_PULLEY_TEETH = 16
_BELT_PITCH = 2 # mm
_PI = 3.14159

_PULLEY_PITCH_RADIUS = _PULLEY_TEETH * _BELT_PITCH / _PI / 2
_TICKS_PER_MM = _PPR / (2 * _PI) / _PULLEY_PITCH_RADIUS
# print(_TICKS_PER_MM)
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
        with open('test_rectangle.hpgl', 'r') as raw_hpgl:
            for line in raw_hpgl:
                split_hpgl = line.split(';')     #split the raw hpgl by the commands at the semi colons
#                 print(split_hpgl)
                
                # This removes all initialize, pen color, and initial pen up commands
                split_hpgl = [ ele for ele in split_hpgl if (ele != 'IN' and ele[:2] != 'SP' and ele != 'PU' and ele != ' ')]
                                
                print(split_hpgl) 
                for ele in split_hpgl:
                    if ele[:2] == 'PU':
                        pen_state = _UP
                    elif ele[:2] == 'PD':
                        pen_state = _DOWN
                    else:
                        print(ele)
                        raise ValueError("something other than PU/PD")
                    coords = ele[2:].split(',')
                    for i in range(0, len(coords), 2):
                        x = int(coords[i]) / 40
                        y = int(coords[i + 1]) / 40
                        th1, th2 = transform(x, y)
                        print(x, y, th1, th2, pen_state)
                        if not self.th1q.full():
                            self.th1q.put(th1)
#                             print(th1)
                            self.th2q.put(th2)
                            self.penq.put(pen_state)
                        
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

    r_1 = ((y_home+y)**2 + (x_home+x)**2)**0.5
    r_2 = ((y_home+y)**2 + (R-x_home-x)**2)**0.5
    
    th1 = int(_TICKS_PER_MM * r_1)
    th2 = int(_TICKS_PER_MM * r_2)

    return(th1, th2)

if __name__ == '__main__':
    import task_share
    th1q = task_share.Queue('i', 1000)
    th2q = task_share.Queue('i', 1000)
    penq = task_share.Queue('i', 1000)
    
    parser = Parser(th1q, th2q, penq)
#     parser = Parser()
    parser.read()
#     print(sp_theta1_queue.get())