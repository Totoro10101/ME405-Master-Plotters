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
    
    with open('eric.csv', 'r') as rawHPGL:
        plotData = []
        for line in rawHPGL:
            commands = []  # store the x y coordinates and pen up and pen down commands
            coordinates = line.split(',')
            for i in range(len(plotData)):
                