"""!
@file task_parser.py
    This file contains a program that parses an HPGL file and then turns it
    into a csv that the nucleo can read.

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
            coord_queue = task_share.Queue()
            
            while i <= len(all_coords):
                if all_coords[i] == 'PU':
                    n = 3
                    coord_queue.put((all_coords[i+1], all_coords[i+2], _up))
                    i = i + 3
                elif all_coords[i] == 'PD':
                    n = 3
                    coord_queue.put((all_coords[i+1], all_coords[i+2], _down))
                    i = i + 3
                else:
                    n = 2
                    coord_queue.put((all_coords[i], all_coords[i+1], all_coords[i]))
            return coord_queue
            print(coord_queue)
            
if __name__ == '__main__':
    parser = Parser()
    parser.read()
    
                