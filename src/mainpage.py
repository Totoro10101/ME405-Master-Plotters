'''!@file       mainpage.py
    Main page for ME 405 Term Project: Master Plotters

    @mainpage

    @section sec_intro  Introduction
                        This is the documentation site for Tori Bornino,
                        Jackson Mclaughlin, and Zachary Stednitz's code used in
                        ME 405 - Mechatronics, Term Project: It's a Plot  
                        Implementation, taught in Winter 2022 by Dr. John 
                        Ridgely. Source code is available at:
                        https://github.com/Totoro10101/ME405-Master-Plotters
    
    @section sec_sch    Software Design
                        Before the pen plotter draws the given image, the plotter
                        is zeroed and the given HPGL is parsed.
                        
                        During general operation the pen plotter has two main tasks:
                        encoder and controller. The encoders running consecutively read 
                        the motor positions and the controller uses the positions to
                        controll the motors. The desired plotter position is loaded
                        during startup. 
                        @image html task_diagram.jpg width=50% \n
                            
    @subsection subsec_sch1 Startup
                            Before the pen plotter plots the drawing, it will zero its position. 
                            Zeroing the encoder is important to ensuring we start plotting the
                            given image at a known location. It utilizes two limit switches to 
                            determine the carriage zero point where the plotter carriage is
                            completely extended. 
                            
                            @image html task_startup_FSM.jpg width=25% \n
                            
    @subsection subsec_sch2 task_parser
                            Parses the HPGL file for a given image outputting the required pen locations in ticks and
                            pen states to construct the drawing. These include "pen advance" and lifting the pen
                            off of the paper when not plotting. Parser task doesn't require a finite state machine
                            since it's only purpose is to read the HPGL data and doesn't transition to any other state.
                            However, the kinematic equations used in the derivation of the transition are further
                            explained in the @ref page_kinetics page.
                            
    @subsection subsec_sch3 task_encoder
                            Reads the position of the encoder on each motor and stores them in a share.
                            This task does not require a finite state machine since it is only reading
                            the position of the motor and the zeroing takes place in the startup task.
                            
    @subsection subsec_sch4 task_controller
                            Controls the motor duty cycle and servo position based on set points stored in the  
                            set point queues. The controller task has two states: Motor and Servo. When a new set
                            point is loaded, the pen condition is checked, and corrected, before transitioning
                            back to the motor state until the next desired position is reached. The controller
                            driver uses PID closed loop control to set the motor duty cycle and move the pen
                            to the desired location. 
                            
                            @image html task_controller_FSM.jpg width=30% \n
                            
    
                            
    @author             Tori Bornino
    @author             Jackson McLaughlin
    @author             Zach Stednitz
    @date               March 15, 2022
'''