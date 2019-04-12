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

    # Sensor states
    _state_init = 0
    _state_on = 1
    _state_off = 2
    _state_count_off = 3
    _state_count_on = 4

    def __init__(self, pir_pin=12, name="PIRSensorThread", notify=None, time_off=300, time_on=2):
        """
        Class constructor.
        :param pir_pin: board pin number where PIR sensor data line is connected.
        :param name: A human readable name for the thread.
        :param notify: Callback for handling sensor state. This method will
        be called on the sensor thread, NOT the current thread.
        :param time_off: The count down value for going to the off state
        :param time_on: The counte down value for going to the on state
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
        # The debounced sensor value (not necessarily the actual sensor value)
        self.sensor_value = 0

        # Sensor value state machine
        self._time_off = time_off
        self._time_on = time_on
        self._sensor_state = self._state_init
        self._count_down_off = self._time_off
        self._count_down_on = self._time_on

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
                # Update the current state of the PIR sensor.
                self._update_sensor()

                if self._notify_proc:
                    self._notify_proc(self.sensor_value)

                # This is why the sensor monitor runs on its own thread.
                time.sleep(1.0)
            logger.debug("Sensor thread terminated")
        except Exception as ex:
            logger.error("PIR Sensor thread terminated by unhandled exception")
            logger.error(ex)

    def _update_sensor(self):
        """
        Update the sensor state machine based on the current value of the sensor.
        The whole purpose of the state machine is to debounce the sensor value,
        thus avoiding false positives or negatives.
        :return: The debounced value of the sensor, true or false.
        """
        # Read the actual state of the PIR sensor.
        # 0 = no movement detected
        # 1 = movement detected
        actual_sensor_value = GPIO.input(self.pir_pin)

        # This is the state machine
        if self._sensor_state == self._state_init:
            # Use the actual sensor value to set the initial state
            if actual_sensor_value:
                self._sensor_state = self._state_on
                self.sensor_value = True
            else:
                self._sensor_state = self._state_off
                self.sensor_value = False
        elif self._sensor_state == self._state_on:
            # Current state is on
            if actual_sensor_value:
                # No state change
                pass
            else:
                # New state is counting down to off
                self._sensor_state = self._state_count_off
                self._count_down_off = self._time_off
        elif self._sensor_state == self._state_off:
            # Current state is off
            if actual_sensor_value:
                # New state is count down to on
                self._sensor_state = self._state_count_on
                self._count_down_on = self._time_on
            else:
                # No state change
                pass
        elif self._sensor_state == self._state_count_on:
            # Current state is counting down to on
            self._count_down_on -= 1
            if actual_sensor_value == self._state_off:
                # New state is off
                self._sensor_state = self._state_off
            elif self._count_down_on > 0:
                # State remains count down to on
                pass
            else:
                # New state is on
                self._sensor_state = self._state_on
                self.sensor_value = True
        elif self._sensor_state == self._state_count_off:
            # Current state is counting down to off
            self._count_down_off -= 1
            if actual_sensor_value:
                # New state is on
                self._sensor_state = self._state_on
            elif self._count_down_off > 0:
                # State remains count down to off
                pass
            else:
                # New state is off
                self._sensor_state = self._state_off
                self.sensor_value = False
        else:
            # Unknown state
            pass

        return self.sensor_value