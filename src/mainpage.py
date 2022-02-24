'''!@file       mainpage.py
    Main page for ME 405 Term Project: Master Plotters

    @mainpage

    @section sec_intro  Introduction
                        This is the documentation site for Tori Bornino,
                        Jackson Mclaughlin, and Zachary Stednitz's code used in
                        ME 405 - Mechatronics, Term Project: It's a Plot  
                        Implementation, taught in Winter 2022 by Dr. John 
                        Ridgly. Source code is available at:
                        https://github.com/Totoro10101/ME405-Master-Plotters
    
    @section sec_sch    Software Design
                        
    
    @subsection subsec_sch1 task_encoder
                            Reads the position of the encoder on each motor and stores them in a share.
                            
    @subsection subsec_sch2 task_startup
                            This task will have the ability to zero the encoder position.
                            Zeroing the encoder is important to ensuring we start plotting the
                            given image at a known location. It will use a limit switch to determine the
                            zero point on the drawing area. 
                            
    @subsection subsec_sch3 task_controller
                            Controls the motor duty cycle based on set points received from the parser task.
                            When a set point is taken from the parser task, it compares the set point to the
                            current encoder position. Then it uses closed loop control to set the motor duty
                            cycle and move the pen to the desired location. This task will read from csv data
                            to move the pen carriage by controlling each motor.
    
    @subsection subsec_sch4 task_parser
                            Parses the HPGL file for a given image and then parses this file for the relevant
                            commands to move the pen carriage. These include "pen advance" and lifting the pen
                            off of the paper when not plotting. 
                         
    @author             Tori Bornino
    @author             Jackson McLaughlin
    @author             Zach Stednitz
    @date               March 15, 2022
'''