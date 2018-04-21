# LumiClock
Copyright © 2018 by Dave Hocker

## Overview
This project is a relatively simple digital clock app that was inspired
by the Lumitime clocks of the '70s and '80s. It uses Python3 and
Tkinter for
the GUI and the Pillow package for implementing an animated GIF.
It was originally conceived as a Raspberry Pi based project.

The clock display takes over the enitre screen. It displays the current time,
an AM/PM indicator and a spinner (an animated GIF). The time display
is sized so that it looks good on a tablet sized display (say 7"-8").

![Screen Shot](https://github.com/dhocker/lumi-clock/raw/master/screenshot.png "Screen Shot")

The app also supports a PIR motion sensor. This allows the app to turn
the clock display on or off based on the motion sensor. This allows
the clock to run 7/24 with reasonable wear on the display.

## Configuration File
The first time you run LumiClock it creates a default configuration file
in a location determined by your OS.

* Windows: C:\Users\username\AppData\Local\lumiclock\lumiclock.conf
* Linux and macOS: ~/lumiclock/lumiclock.conf

The configuration file contains settings for several items.
* font: The default font is Courier New. A fixed pitch font works best.
A good mono-space digital font is
["Digital-7 Mono"](https://www.dafont.com/digital-7.font).
* fontsize: Sets the size of the font in pixels. The default is
(45%) * (screen height). On the Raspberry Pi touchscreen this is
0.45 * 480 = 216px.
* color: Sets the foreground color of the font. The default color
is "#EC3818" which is an approximation of the color of the original
Lumitime clock's digits. This color does not affect the spinner.
* spinner: Selects the default GIF file for the spinner. The
default is "spiral_triangles.gif". There are a number of GIF files
in the project directory.
* loglevel: Selects the level of logging (debug, warning, info, error)
The default is "debug".
* pirsensor: Determines if a PIR motion sensor is present. Use a
value of "True", "on" or 1 to indicate one is present. Use "False",
"off" or 0 otherwise. This setting allows you to run LumiClock on
a Raspberry Pi without a PIR sensor.
* timeout: Sets the display timeout value in minutes. This is only
meaningful if you have a PIR motion sensor. This is how long the
display will stay on once the PIR sensor indicates no motion.
* debugdisplay: Logs detailed information about display
management. This is useful for determining if the PIR sensor is
functioning as expected. Use a
value of "True", "on" or 1 to enable. Use "False",
"off" or 0 otherwise.

## Spinner
The spinner is a 128x128 animated GIF. The project includes several
spinners that were generated with the default color (#EC3818). You can
generate your own spinners and place them in the project directory.
[Chimply](http://www.chimply.com/Generator) is a good site for
generating animated GIFs.

## User Interface
Touching the screen or a left mouse click will cause a context menu
to be shown. The context menu contains a list of the spinner GIFs
that are available and other program actions (like Quit). Any GIF in
the project directory will be shown on the context menu. Thus, if you
add your own GIFs they will show on the context menu.

![Context Menu](https://github.com/dhocker/lumi-clock/raw/master/contextmenu.png "Context Menu")

## Building a Clock
TBD - picture of finished project
### Hardware
#### BOM
* Display: [Adafruit 7" touchscreen][Display]
* Raspberry Pi: Model 3B or 3B+ (with WiFi)
* PIR sensor: [Adafruit PIR motion sensor][PIRSensor]
* SDcard: 8GB or larger

#### Wiring Diagram

![Wiring Diagram](https://github.com/dhocker/lumi-clock/raw/master/LumiClock%20Wiring%20Diagram.png "Wiring Diagram")

### Software
#### BOM
* OS: Raspbian Stretch
* Python3: Version >= 3.5
* Tkinter: Version >= 8.6
* Pillow: Version >= 5.0

#### Setup

##### Disable Display Sleep
[Reference][Adjusting Display]

By default, the desktop will put the display to sleep after a short
time with no activity. For LumiClock to behave reasonably you can
disable the sleep function. Unfortunately, this is not as simple as
it should be.

You need to edit the /etc/lightdm/lightdm.conf file
```
sudo nano /etc/lightdm/lightdm.conf
```
and add the following.

```
[SeatDefaults]
xserver-command=X -s 0 dpms
```

##### Change Display Brightness
[Reference][Adjusting Display]

LumiClock can do with less than full backlight brightness. To change
the brightness use this command.
```
sudo bash -c "echo n > /sys/class/backlight/rpi_backlight/brightness"
```
where 0 <= n <= 255.

A value of 128 seems to work nicely.

## References
* [Example](https://www.youtube.com/watch?v=hhVlHwHnsEg) - examples of
Lumitime clocks.
* [History](http://www.objectplastic.com/2009/03/lumitime-clock-various-designers-tamura.html) -
some of the story behind the Lumitime clock.
* [Display](https://www.adafruit.com/product/2718) - an 800x480 touchscreen
that can be combined with a Raspberry Pi to build a clock.
* [PIRSensor](https://adafruit.com/product/189) - an inexpensive module
that is easy to use.
* [Digital Font](https://www.dafont.com/digital-7.font) - a nice digital (7 segment)
font.
* [Chimply](http://www.chimply.com/Generator) - a good site for generating
animated GIFs.
* [Adjusting Display](https://raspberrypi.stackexchange.com/questions/46225/adjusting-the-brightness-of-the-official-touchscreen-display) -
how to turn the display backlight on/off and adjust its brightness.
