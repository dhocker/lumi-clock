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

from pir_sensor_thread import SensorThread
import time


if __name__ == '__main__':
    print("Press ctrl-C to terminate")
    threadinst = SensorThread()
    try:
        threadinst.start()
        print(threadinst.name)
        # Wait until human presses ctrl-C
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        print()
        print("Keyboard interrupt")
    except Exception as ex:
        print("Unhandled exception")
        print(ex)
    finally:
        print("Terminating sensor thread")
        threadinst.terminate()

    print("End")
