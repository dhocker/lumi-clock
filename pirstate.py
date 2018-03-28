#
# Adafruit PIR sensor state machine testing
# http://adafruit/189
#
# The sensor monitor needs to run on its own thread so that
# it is not subject the behaviour of tkinter.
#
# How to turn display on and off
# https://scribles.net/controlling-display-backlight-on-raspberry-pi/
#
# echo 1 | sudo tee /sys/class/backlight/rpi_backlight/bl_power
# echo 0 | sudo tee /sys/class/backlight/rpi_backlight/bl_power
#

import RPi.GPIO as GPIO
import time
import datetime

pir = 12
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pir, GPIO.IN)

# states
display_off = 0
display_on = 1
display_count_down = 2
display_state = display_off
count_down_time = 60 * 1
down_counter = 0

try:
    change_time = datetime.datetime.now()
    while True:
        now = datetime.datetime.now()
        v = GPIO.input(pir)
        
        if display_state == display_off:
            if v:
                # new state is on
                print("Display on")
                display_state = display_on
        elif display_state == display_on:
            if not v:
                # New state is counting down
                print("Counting down to display off")
                down_counter = count_down_time
                display_state = display_count_down
        elif display_state == display_count_down:
            # Counting down to display off
            down_counter -= 1
            if down_counter <= 0:
                # New state is display off
                print("Display off")
                display_state = display_off
            elif v:
                # New state is display on
                print("Display on")
                display_state = display_on
            else:
                # Maintain same state
                pass
        else:
            # Unknown state
            print("Unknown state", display_state)
        
        print(display_state)
        time.sleep(1.0)
except:
    print()
    print("Keyboard interrupt")

print("End")

