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
        new_coords = []
        plot_array = []
        for i in range(len(all_coords)):
            if 'IN' in all_coords[i]:
                # print("Initialize")
                pass
            elif 'PU' in all_coords[i]:
                # print("Pen Up")
                sep = all_coords[i].split('PU') # Removes PU from the command, will replace with 0
                sep[0] = str(0)  # Pen is not touching the paper
                # print(sep)
                if sep[1] is '': # Pass the element if it is empty after split
                    pass
                else:
                    new_coords.append(sep[0])  # Add pen up command to the new coordinates
                    new_coords.append(sep[1])  # Add the coordinate associated with it.
            elif 'SP1' in all_coords[i]:
                # print("Select Pen")
                pass
            elif 'PD' in all_coords[i]:
                # print("Pen Down")
                sep2 = all_coords[i].split('PD') # Removes PD and replaces with 1 to indicate pen is touching paper
                sep2[0] = str(1)
                # print(sep2)
                new_coords.append(sep2[0])
                new_coords.append(sep2[1])
            else:
                new_coords.append(all_coords[i])
        print(new_coords)
        
if __name__ == '__main__':    
    read()
                