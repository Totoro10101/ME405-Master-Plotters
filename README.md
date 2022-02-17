# ME405 Master Plotters
### A ME 405 term project that documents a pen plotter design.

The design we're going with is inspired by this YouTube video by DAZ projects: 

[the SIMPLEST cnc PEN PLOTTER | how to build it](https://www.youtube.com/watch?v=zFRRUZdz1HY)

Although we're taking inspriation from this design, we are making some changes to the design that we believe will improve 
the plotter. The basic layout of this design is a 2.5-D pen plotter that is laid out horizontally on a flat base. The base is
is going to be a rectangular plywood piece with pulleys at each corner. There will be two gear motors driving the pen plotter placed
at two adjacent corners (see sketch). The two motors will direct drive the two pulleys at the corners of the base, and the two other 
pulleys will control the tension of the belt. Instead of using string and bungey cord like the video, we will use a GT2 timing belt
to increase the traction on the pulley because of the gearing present on the pulley wheels and the belts. To actuate the pen and lift it
off of the paper of moving between intermediate lines, we'll use a small solenoid that activates to lift the pen. Thep pen's resting
position is on the table, so the solenoid will only activate in between drawings.

A rough bill of materials is shown below. We're keeping the main motors simple by using the equipment available to us in lab. The GT2 belt and
pulleys will be purchased from Amazon and other components to hold the pen will be 3D printed by our group. 


| Qty. | Part                  | Source                | Est. Cost |
|:----:|:----------------------|:----------------------|:---------:|
|  2   | Pittperson Gearmotors | ME405 Tub             |     -     |
|  1   | Nucleo with Shoe      | ME405 Tub             |     -     |
|  1   | Purple Sharpie&trade; | Office Min&trade;     |   $1.02   |
|  2   | 5A Power MOSFET       | Doggy-Key             |   $2.34   |
|  3   | Rubber Gaskets        | Dumpster Behind Bondo | Our pride |