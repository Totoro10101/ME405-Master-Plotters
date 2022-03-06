"""!
@file task_parser.py
    This file contains a program that parses an HPGL file and then turns it
    into a csv that the nucleo can read.

@author             Tori Bornino
@author             Jackson McLaughlin
@author             Zach Stednitz
@date               March 15, 2022

"""

def read():
    ''' @brief   Reads data from a hpgl file.
        @details Reads each line of data and ignores input not relevant to the pen's position.
                 Takes the data points and converts them to a readable format to send to our
                 controller for setting set points for our motors.
    '''
    with open('test_spiral.hpgl', 'r') as raw_hpgl:
        split_hpgl = []
        separate_commands = []
        all_coords = []
        continuous_coords = []
        for line in raw_hpgl:
            split_hpgl = line.split(';')     #split the raw hpgl by the commands at the semi colons
            for i in range(len(split_hpgl)):        # go through the list that the split creates
                separate_commands = split_hpgl[i].split(',')  # split the individual items in the list s
                                                              # since HPGL puts out long continuous commands
                                                              # as a csv essentially.
                print(separate_commands)
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
        
if __name__ == '__main__':    
    read()
                