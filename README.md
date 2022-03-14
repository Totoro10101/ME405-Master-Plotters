# ME405 Master Plotters
### A ME 405 term project that documents a pen plotter design.

The design we're going with is inspired by this YouTube video by DAZ projects: 

[the SIMPLEST cnc PEN PLOTTER | how to build it](https://www.youtube.com/watch?v=zFRRUZdz1HY)

Although we're taking inspriation from this design, we are making some changes that we believe will improve
its performance. The basic layout of this design is a 2.5-D pen plotter that is laid out horizontally on a flat base. The base is
is going to be a rectangular plywood piece with pulleys at each corner. There will be two gearmotors driving the pen plotter placed
at two adjacent corners (see sketch). The two motors will directly drive the two pulleys at the corners of the base, and the two other 
pulleys will be idlers which guide the belt. They will make the belt form one continuous loop in an hourglass shape.
Instead of using string like the video, we will use a GT2 timing belt to increase the traction on the pulley because of the teeth
present on the pulley wheels and the belts, and eliminate slipping. Since the total length of the belt will change slightly as the pen moves,
we will use a stretchy paracord joined with the timing belt to provide some room for movement while keeping tension. To actuate the pen and lift it
off of the paper when moving between drawn lines, we'll use a small servo that activates to lift the pen within its holder. This holder will have
ball rollers on the bottom to allow it to move smoothly over the paper.

A rough bill of materials is shown below. We're keeping the main motors simple and efficient by using the equipment available to us in lab. The GT2 belt and
pulleys will be purchased from Amazon and other components to hold the pen and servo and to mount the motors will be 3D printed by our group.

## Bill of Materials
| Qty. | Part                           | Source                | Est. Cost |
|:----:|:-------------------------------|:----------------------|:---------:|
|  2   | Pittperson Gearmotors          | ME405 Tub             |     -     |
|  1   | Nucleo with Shoe               | ME405 Tub             |     -     |
|  1   | GT2 Timing Belt                | Amazon                |   $6.99   |
|  1   | GT2 Timing Pulleys             | Amazon                |   $7.99   |
|  1   | Mini Ball Transfer Bearing     | Amazon                |   $10.95  |
|  6   | Skateboard Bearings            | Jackson               |     -     |
|  1   | Sunfounder Micro Servo         | Charlie               |     -     | 
|  1   | Bungee Cord 1/8" Diameter      | Amazon                |   $5.95   | 
|  1   | Small String                   | Tori                  |     -     |


## Preliminary System Sketch
| ![Plotter System](images/scaledsketch.png) |
|:--:|
|**Figure 1: Scaled sketch showing the basic layout of our planned plotter**|

## Hardware Design
| ![Plotter System](images/cadmodel.png) |
|:--:|
|**Figure 2: CAD Model showing final version of Pen Plotter**|

The hardware we are using is mostly 3D printed from CAD designs created in Solidworks. The main components are the motor mounts, paracord pulleys, 
the pen carriage, and servo mount for actuating the pen.

## Software Design
The software we designed uses a task based approach to update encoder positions and control set points based on a given HPGL file. The first process
to run is the start up process that zeros our encoders and puts the pen carriage in a known home position for us to use as a reference point to calculate 
set points from the HPGL file. The parsed HPGL file gives coordinates in the form of encoder ticks using a coordinate transformation that calculates it 
based on the HPGL and then sets the set point for each motor individually. The controller and encoder constantly update and share the data they collect
to tell whether the pen has reached the proper set point. 

For more detailed explanation on the tasks being performed, refer to our [Github Pages Documentation](https://totoro10101.github.io/ME405-Master-Plotters/)

## Results
The results of our pen plotter were very encouraging. By the end of thep project, we were able to perform relatively complex drawings that included both 
straight lines and curves, pen up and pen down commands, and could be taken from any file drawn in Inkscape so long as there were no memory issues with the
HPGL and the Nucleo. 

We tested the functionality of our pen plotter by providing it with multiple different HPGL files that we believed covered all the important aspects of the 
machine. We needed a file that would move in straight lines as well as curves and also required the lifting of the pen between operations. So long as the 
plotter was able to perform all of these tasks and draw the desired shapes, we believed it would be robust enough of a design to handle any HPGL file. 
The system performed fairly well in these tests once we got the controller set points and kinematics all correct. One minor issue is that the device moves 
more quickly in the direction that the bungee is pulling it in, so it was a little bit less accurate in that direction. Another thing we noticed in testing the 
plotting was that the Inkscape HPGL included a feature to run over all line commands twice, so it would draw something, and then attempt to go right back over it 
for a darker drawing. This functionality showed us that it wasn't perfectly repeatable due to some steady state error and overshoot in our controller or the bungee
affecting the path too much for repeatability, so the second time a line was plotted, it wasn't perfectly overlapping the original line. This could be fixed with 
some more tuning to controller gains or bungee length, but the variation in repeatability was small enough for our uses.

In the future, if we were to revisit this design or give recommendations for others attempting the same system, we would focus on 

## Additional Links





