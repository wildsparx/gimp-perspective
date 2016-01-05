# gimp-perspective
Plugins for perspective drawing in GIMP

Copyright (C) 2015 Asher Blum

http://wildsparx.com/gimp-perspective/

## Installation

On Linux and Mac, find your gimp plugins directory, such as ~/gimp-2.8/plug-ins

cp *.py ~/gimp-2.8/plug-ins

restart gimp

## perspective-ellipse

Draws ellipses to represent horizontal circles. Can also draw vertical lines
to complete a wireframe of a vertical cylinder such as a round tower.

* Ellipses are proportioned based on distance from horizon line.

## Using perspective-ellipse
* Draw a horizon line across your image; note the y-coordinate
* Set the brush and foreground color for the ellipses you want.

### Draw a Single Ellipse
* Use the rectangle select tool to draw the major axis of the ellipse
* The top line of the rectangle becomes the major axis
* The rest of the rectangle doesn't matter - keep it short vertically
* Choose Tools/Perspective/Ellipses
* Enter the height of your horizon line in "Horizon Height"
* Click OK
* The plugin creates a new layer with one ellipse on it.

### Draw Multiple Independent Ellipses
* Use the rectangle select tool to draw the major axis of the first ellipse
* Put the select tool in "Add" mode 
* Add more rectangles to the selection
* Call the plugin - same as for a single ellipse

### Draw a Vertical Cylinder
* Use the rectangle select tool to select the whole cylinder as a rectangle
* Choose Tools/Perspective/Ellipses
* Set vertical spacing to about 1/10 the height of the cylinder
* Set "Draw vertical lines" to Yes
* Click OK

## Using perspective-grid
* Use just once while setting up drawing
* Set the brush size and hardness, for example size 4, hardness 50
* Choose Tools/Perspective/Grid
* Set the vanishing points off the canvas an appropriate amount
* Set the horizon height to where you want the horizon line - use the scale at the left edge of the canvas.
* Click OK


## perspective-extract

Extracts the perspective grid from an existing image

