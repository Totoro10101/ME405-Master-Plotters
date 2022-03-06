'''!
@file transformation.py
This file contains the derivation for the transformation used to convert points
in the image to angles for motors 1 and 2.
'''

# These define the geometry of the board
R = 263 #mm             # Distance between the motors
r_max = 330 #mm         # Distance from one motor to the opposite far corner of the drawing area
# The drawing area is 4 in by 6 in.
x_lim = 4 * 25.4 #mm    
y_lim = 6 * 25.4 #mm

# First we find the location of the bottom left corner by transforming 2 in to the left
r_2_star = (r_max**2 - (2*R*(x_lim/2)))**(0.5)
print(r_max, r_2_star)

# Then we find the location of HOME by tracing the 6 in on the left side of the drawing area
s = (r_max + r_2_star + R)/2
A = (s*(s-r_max)*(s-r_2_star)*(s-R))**0.5

y_prime = 2*A/R
x_prime = (r_max**2 - y_prime**2)**0.5
print(x_prime, y_prime)

r_1_home = ( (y_prime-y_lim)**2 + x_prime**2)**0.5
r_2_home = ( (y_prime-y_lim)**2 + (R-x_prime)**2)**0.5
print(r_1_home, r_2_home)

s_home = (r_1_home + r_2_home + R)/2
A_home = (s_home*(s_home-r_1_home)*(s_home-r_2_home)*(s_home-R))**0.5

y_home = 2*A_home/R
x_home = (r_1_home**2 - y_home**2)**0.5
print(x_home, y_home)


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
