''' @file                page_kinetics.py
    @brief               Page describing the transform used to convert from (x,y) to (theta_1, theta_2).
    
    \page transform Kinemmatic Derivations of Transform
    
     
     As shown in the sketch below, the drawing area is defined such that the
     fully extended radius of each motor reaches the far corner of the drawing
     area. This forces the "zeroed" position of the carriage to be beyond the
     drawing area.
     
     Our transform is based off of the top left corner of the drawing area.
     For the described "zeroed" position and an assumed 4 in x 6 in drawing area,
     the location of the "home" position (the top left corner) is given as
     x_home = 80.7 mm and y_home = 122.676 mm. 
    
    \image html homePosition.png width=50% \n
    
    At this point, if we treat each radius as the hypotenuse of a right triangle,
    where the (y_home + y) position is the height of the triange, and the
    (x_home + x) is the base of the triangle for the right triangle, and
    (R - (x_home + x)) is the base of the second triangle when R is the distance
    between the two motors, then we can compute the new radii using the
    pythagorean theorem:
        - r_1 = ((y_home + y)**2 + (R - (x_home + x))**2)**0.5
        - r_2 = ((y_home + y)**2 + (x_home + x)**2)**0.5
        
    From here, we know that the belt length per revolution is:
        r = 16 [teeth] * 2 [mm/tooth] = 32mm
    We also know that the encoder pulses (ticks) per revolution is:
        ppr =     256 [counts per revolution]
                * 4   [pulses per count for quadrature encoders]
                * 16  [16:1 gear ratio]
    Therefore we have the ticks per mm ratio as:
        ppr / r = 512 [ticks/mm]

    So we have the final output (theta_1, theta_2) in ticks:
        th1 = int(TICKS_PER_MM * r_1)
        th2 = int(TICKS_PER_MM * r_2)

'''
