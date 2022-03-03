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
    # Empty lists for data
    # Inspired by this website's article on plotting csv files
    # https://www.geeksforgeeks.org/visualize-data-from-csv-file-in-python/
    x = []
    y = []
    
    # Read the csv file.
    # Made with reference to this stackoverflow post that shows how to use the split command
    # to separate data in the csv
    # https://stackoverflow.com/questions/32327936/how-to-load-data-from-a-csv-file-without-importing-the-csv-module-library
    # Open the HGPL file and read the data from it
    with open('eric.csv', 'r') as rawHPGL:
        plotData = []
        for line in rawHPGL:
            commands = []  # store the first two valid data columns (no strings)
            numbers = line.split(',')
            for i in range(len(plotData)):
                try:
                    if float(numbers[i]): # Determine if valid input
                        commands.append(plotData[i]) # Add valid inputs to the two column list for graphing
                except ValueError:
                    pass                  # Pass incorrect inputs such as strings or blank space
            x.append(commands[0])
            y.append(commands[1])