#
# Adafruit PIR sensor state machine on a thread
# http://adafruit/189
#
# The sensor monitor needs to run on its own thread so that
# it is not subject the behaviour of anything else like tkinter.
#
# How to turn official 7" touchscreen display on and off
# https://scribles.net/controlling-display-backlight-on-raspberry-pi/
#
# OFF
# echo 1 | sudo tee /sys/class/backlight/rpi_backlight/bl_power
# ON
# echo 0 | sudo tee /sys/class/backlight/rpi_backlight/bl_power
#
# And, how to do it for an HDMI attached display.
#
# OFF
# vcgencmd display_power 0
# ON
# vcgencmd display_power 1

import RPi.GPIO as GPIO
import time
import threading
import subprocess
from display_controller import DisplayController
from app_logger import AppLogger


# Logger init
the_app_logger = AppLogger("lumiclock")
logger = the_app_logger.getAppLogger()


class SensorThread(threading.Thread):
    """
    Thread based class for working with the Adafruit PIR sensor.
    This class can be used as-is or it can be used as the base
    class for a more customized implementation.
    Reference: http://adafruit/189

    The initial state is unknown.
    """
    def __init__(self, pir_pin=12, name="PIRSensorThread", notify=None):
        """
        Class constructor.
        pir_pin: board pin number where PIR data line is connected.
        count_down_time: in seconds, how long to wait before entering the
            display off state.
        name: A human readable name for the thread.
        """
        threading.Thread.__init__(self, name=name)
        # Using pin 12 (GPIO 18) for PIR sensor signal
        self.pir_pin = pir_pin
        # Using board numbering as opposed to BCM numbering
        GPIO.setmode(GPIO.BOARD)
        # Using pin for input only
        GPIO.setup(self.pir_pin, GPIO.IN)

        self._notify_proc = notify
        self._terminate_thread = False

        # Public properties
        self.sensor_value = 0

    def run(self):
        """
        Override to call the sensor monitoring code
        on its own thread. Technically, this can be overriden by
        a derived class. The overriden method should call the base
        class if it wants the sensor monitor to run.
        """
        self.run_sensor()
        
    def terminate(self):
        """
        Called to terminate the sensor monitor thread.
        """
        # This variable is a simple semaphore. There are no
        # multi-threading issues as the variable is only
        # read on the sensor thread.
        self._terminate_thread = True
        self.join()

    def run_sensor(self):
        """
        Monitors the PIR sensor. Expects to be called on
        its own thread.
        """

        while not self._terminate_thread:
            # Read the current state of the PIR sensor.
            # 0 = no movement detected
            # 1 = movement detected
            self.sensor_value = GPIO.input(self.pir_pin)

            if self._notify_proc:
                self._notify_proc(self.sensor_value)

            # This is why the sensor monitor runs on its own thread.
            time.sleep(1.0)
        logger.debug("Sensor thread terminated")
