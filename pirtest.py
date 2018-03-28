#
# Adafruit PIR sensor testing
# http://adafruit/189
#
# The sensor monitor needs to run on its own thread so that
# it is not subject the behaviour of tkinter.
#

import RPi.GPIO as GPIO
import time
import datetime

pir = 12
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pir, GPIO.IN)

try:
    change_time = datetime.datetime.now()
    last_v = GPIO.input(pir)
    on_time = 0
    display_state = False
    default_on_time = 60 * 15
    while True:
        now = datetime.datetime.now()
        v = GPIO.input(pir)
        if last_v != v:
            # Sensor changed
            elapsed = now - change_time
            change_time = now
            if v:
                # Sensor now on
                on_time = default_on_time
                display_state = True
                print(now.strftime("%H:%M:%S"), v, "display turned on", elapsed.seconds)
            else:
                # Sensor now off
                print(now.strftime("%H:%M:%S"), v, "for", elapsed.seconds)
        else:
            # Sensor unchanged
            if not v:
                # Sensor off, run timer
                if on_time:
                    on_time -= 1
                if on_time <= 0 and display_state:
                    # display turns off
                    display_state = False
                    print(now.strftime("%H:%M:%S"), "display turned off", v)
                else:    
                    print(now.strftime("%H:%M:%S"), v, on_time)
            else:
                # Sensor on
                on_time = default_on_time
                print(now.strftime("%H:%M:%S"), v)
        last_v = v
        time.sleep(1.0)
except:
    print()
    print("Keyboard interrupt")

print("End")
