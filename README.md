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
we will use a stretchy rubber band joined with the timing belt to provide some room for movement while keeping tension. To actuate the pen and lift it
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
|  4   | Bronze Bushings                | ME 405 Tub            |     -     |
|  1   | Sunfounder Micro Servo         | Charlie               |     -     | 
|  1   | BongoTies Bungie Cord          | Senior Project        |     -     | 

## System Sketch
| ![Plotter System](plots/scaledsketch.png) |
|:--:|
|**Figure 1: Scaled sketch showing the basic layout of our planned plotter**|
