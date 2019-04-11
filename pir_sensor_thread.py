# -*- coding: UTF-8 -*-
#
# Copyright © 2018, 2019  Dave Hocker (email: athomex10@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the LICENSE.md file for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program (the LICENSE.md file).  If not, see <http://www.gnu.org/licenses/>.
#
# The sensor monitor needs to run on its own thread so that
# it is not subject the behaviour of anything else like tkinter.
#

import RPi.GPIO as GPIO
import time
import threading
from app_logger import AppLogger


# Logger init
the_app_logger = AppLogger("lumiclock")
logger = the_app_logger.getAppLogger()


class SensorThread(threading.Thread):
    """
    Thread based class for working with a 3 pin PIR sensor.
    This class can be used as-is or it can be used as the base
    class for a more customized implementation.
    Reference: http://adafruit/189

    The initial state is unknown.
    """
    def __init__(self, pir_pin=12, name="PIRSensorThread", notify=None):
        """
        Class constructor.
        :param pir_pin: board pin number where PIR sensor data line is connected.
        :param name: A human readable name for the thread.
        :param notify: Callback for handling sensor state. This method will
        be called on the sensor thread, NOT the current thread.
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

        try:
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
        except Exception as ex:
            logger.error("PIR Sensor thread terminated by unhandled exception")
            logger.error(ex)
