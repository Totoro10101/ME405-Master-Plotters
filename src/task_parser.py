"""!
@file task_parser.py
    This file contains a program that parses an HPGL file and then turns it
    into a format that contains the location of x and y and pen commands.

@author             Tori Bornino
@author             Jackson McLaughlin
@author             Zach Stednitz
@date               March 15, 2022

"""
import pyb
import task_share

class Parser:
    
    def __init__(self):
        self._up = 0
        self._down = 1

    def read(self):
        ''' @brief   Reads data from a hpgl file.
            @details Reads each line of data and ignores input not relevant to the pen's position.
                     Takes the data points and converts them to a readable format to send to our
                     controller for setting set points for our motors.
        '''
        with open('test_rectangle.hpgl', 'r') as raw_hpgl:
            split_hpgl = []
            separate_commands = []
            all_coords = []
            continuous_coords = []
            for line in raw_hpgl:
                split_hpgl = line.split(';')     #split the raw hpgl by the commands at the semi colons
                # print(split_hpgl)
                for i in range(len(split_hpgl)):
                    if 'IN' in split_hpgl[i]:
                        # print("Initialize")
                        pass
                    elif 'PU' in split_hpgl[i]:
                        # print("Pen Up")
                        sep = split_hpgl[i].split('PU') # Removes PU from the command, will replace with 0
                        sep[0] = 'PU'  # Pen is not touching the paper
                        # print(sep)
                        if sep[1] is '': # Pass the element if it is empty after split
                            pass
                        else:
                            separate_commands.append(sep[0])
                            separate_commands.append(sep[1])
                    elif 'SP1' in split_hpgl[i]:
                        # print("Select Pen")
                        pass
                    elif 'PD' in split_hpgl[i]:
                        # print("Pen Down")
                        sep2 = split_hpgl[i].split('PD') # Removes PD and replaces with 1 to indicate pen is touching paper
                        sep2[0] = 'PD'
                        # print(sep2)
                        separate_commands.append(sep2[0])
                        separate_commands.append(sep2[1])
                    else:
                        separate_commands.append(split_hpgl[i])
                        # split the individual items in the list s
                        # since HPGL puts out long continuous commands
                        # as a csv essentially.
            # print(separate_commands)
            for j in range(len(separate_commands)): # iterate through the list created by splitting at the commas
                if len(separate_commands) >= 2:      # if it's got a length of more than 2, it shows that the pen plotter will be
                                                    # continuously moving in that pen state
                    continuous_coords = separate_commands[j].split(',') # split it so you can add the to a master list
                                                                        # of all the commands from the HPGL
                    for m in range(len(continuous_coords)):
                        all_coords.append(continuous_coords[m])  # add the separated coords to 
                else:
                    for n in range(len(separate_commands)):
                        all_coords.append(separate_commands[n])  # further split the values to not put lists inside of lists
            print(all_coords)
            
            # Process the all_coords list to put it into a list that is structured as
            # (r1, r2, pen) where the radiuses will determine how much to spin the motor
            # and pen will indicate whether it is up or down.
            
            n = 3
            i = 0
            _prev_com = self._up  # Stores the previous pen command of up or down
            _r_pulley = 16*2/3.14159    # mm
            _PPR = 256*4*16
            coord_queue = task_share.Queue('i', 10000, thread_protect = True, overwrite = False)
            
            while i <= len(all_coords):
                if all_coords[i] == 'PU':  
                    n = 3
                    x1 = int(all_coords[i+1])/40  #convert dpi from hpgl to mm
                    y1 = int(all_coords[i+2])/40
                    calc = transform(x1,y1)
                    r1 = calc[0]
                    r2 = calc[1]
                    theta_rad1 = r1/_r_pulley
                    theta_rad2 = r2/_r_pulley
                    tix1 = theta_rad1*_PPR
                    tix2 = theta_rad2*_PPR
                    coord_queue.put((tix1, tix2, self._up))
                    _prev_com = self._up
                    i = i + 3
                elif all_coords[i] == 'PD':
                    n = 3
                    x1 = int(all_coords[i+1])/40
                    y1 = int(all_coords[i+2])/40
                    calc = transform(x1,y1)
                    r1 = calc[0]
                    r2 = calc[1]
                    theta_rad1 = r1/_r_pulley
                    theta_rad2 = r2/_r_pulley
                    tix1 = theta_rad1*_PPR
                    tix2 = theta_rad2*_PPR
                    coord_queue.put((tix1, tix2, self._down))
                    _prev_com = self._down
                    i = i + 3
                else:
                    n = 2
                    x1 = int(all_coords[i])/40
                    y1 = int(all_coords[i+1])/40
                    calc = transform(x1,y1)
                    r1 = calc[0]
                    r2 = calc[1]
                    theta_rad1 = r1/_r_pulley
                    theta_rad2 = r2/_r_pulley
                    tix1 = theta_rad1*_PPR
                    tix2 = theta_rad2*_PPR
                    coord_queue.put((tix1, tix2, _prev_com))
                    i = i + 2
            return coord_queue

R = 263 #mm             # Distance between the motors
y_home = 2*A_home/R
x_home = (r_1_home**2 - y_home**2)**0.5

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

    r_1_pprime = ( (y_home+y)**2 + (x_home-x)**2)**0.5
    r_2_pprime = ( (y_home+y)**2 + (R-(x_home-x))**2)**0.5

    return(r_1_pprime, r_2_pprime)

if __name__ == '__main__':
    parser = Parser()
    parser.read()
    
                