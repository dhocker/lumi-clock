# -*- coding: UTF-8 -*-
#
# Raspberry Pi display controller
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
#

import threading
import subprocess
import platform
import rpi_backlight
from app_logger import AppLogger

# Logger init
the_app_logger = AppLogger("lumiclock")
logger = the_app_logger.getAppLogger()


class DisplayController:
    """
    The display is controlled by a state machine.
    Display off
    Display on
    Count down to display off
    Count down to display on
    Unknown

    """

    # states
    _state_unknown = 0
    _state_display_off = 1
    _state_display_on = 2
    _display_states = ["unknown", "off", "on"]

    # Serializes access to the display
    _display_lock = threading.Lock()
    _backlight_state = 0

    # A singleton instance of the backlight class
    _backlight = None

    def __init__(self):
        """
        Class constructor.
        count_down_time: in seconds, how long to wait before entering the
            display off state.
        """

        # This path needs to be determined based on machine/OS version
        # This value works for RPi OS Desktop 64-bit aarch64.
        # It will not work for 32-bit OSes.
        if DisplayController._backlight is None:
            backlight_path = DisplayController.get_backlight_path()
            if backlight_path is None:
                _backlight = None
            elif backlight_path != "":
                _backlight = rpi_backlight.Backlight(backlight_path)
            elif backlight_path == "":
                _backlight = rpi_backlight.Backlight()
            else:
                logger.error("Could not resolve location of backlight")

        self._display_state = DisplayController.query_display_state()

    """
    The techniques used to manage diffrent displays was
    found at: https://scribles.net/controlling-display-backlight-on-raspberry-pi/
    """
    
    def set_display_state(self, sensor_value):
        """
        Display management state machine
        :param sensor_value: The current debounced value of the PIR sensor
        :return: None
        """
        if self._display_state == self._state_display_off:
            # Current state is display off
            if sensor_value:
                # New state is on
                self._display_state = self._state_display_on
                self.display_on()
            else:
                pass
        elif self._display_state == self._state_display_on:
            # Current state is display on
            if not sensor_value:
                # New state is off
                self._display_state = self._state_display_off
                self.display_off()
            else:
                pass
        else:
            # Unknown state
            logger.debug("Undefined state %s", self._display_state)

    def get_display_state(self):
        return self._display_states[self._display_state]

    @staticmethod
    def is_hdmi_display():
        """
        Answers the question: Is the current display HDMI?
        Otherwise, it is assumed to be the RPi 7" touchscreen.
        """
        try:
            res = subprocess.run(["tvservice", "-s"], stdout=subprocess.PIPE)
            res = str(res.stdout, 'utf-8')
            if res.find("HDMI") != -1:
                return True
            return False
        except:
            pass
        return False

    @staticmethod
    def is_raspberry_pi():
        # A weak test for the RPi
        return platform.machine() in ["armv7l", "armv8l", "aarch64"]

    @staticmethod
    def get_backlight_path():
        """
        Return the path to the backlight for this machine. This method was
        necessitated by RPi OS 64-bit which changed the path to the backlight.
        :return:
        """
        if DisplayController.is_raspberry_pi():
            if platform.machine() in ["aarch64"]:
                return "/sys/class/backlight/10-0045"
            return ""
        return None

    """
    These methods can be overriden in a derived class
    to provide advanced customization of each state.
    Each method is called when the state is entered.
    """

    def display_on(self):
        self.turn_display_on()

    def display_off(self):
        self.turn_display_off()

    def display_off_count_down(self):
        logger.debug("Starting count down to display off from %d", self.off_counter)

    def display_off_counting_down(self):
        if (self.off_counter % 30) == 0:
            logger.debug("Counting down to display off %d", self.off_counter)

    def display_on_count_down(self):
        logger.debug("Starting count down to display on from %d", self.on_counter)

    def display_on_counting_down(self):
        if (self.on_counter % 30) == 0:
            logger.debug("Counting down to display on %d", self.on_counter)

    """
    The techniques used to manage diffrent displays was
    found at: https://scribles.net/controlling-display-backlight-on-raspberry-pi/
    Note that these are class methods because there is only one physical display.
    """

    @classmethod
    def query_display_state(cls):
        cls._display_lock.acquire()
        state = cls._state_unknown
        if DisplayController.is_raspberry_pi():
            if DisplayController.is_hdmi_display():
                # subprocess.run(["vcgencmd", "display_power", "1"])
                state = cls._state_unknown
            else:
                # rpi 7" touchscreen
                if cls._backlight.power:
                    state = cls._state_display_on
                else:
                    state = cls._state_display_off
        else:
            pass
        cls._display_lock.release()
        logger.debug("Current display state %s", cls._display_states[state])
        return state

    @classmethod
    def turn_display_on(cls):
        cls._display_lock.acquire()
        if DisplayController.is_raspberry_pi():
            if DisplayController.is_hdmi_display():
                subprocess.run(["vcgencmd", "display_power", "1"])
            else:
                # rpi 7" touchscreen
                # a = "echo 0 | sudo tee /sys/class/backlight/rpi_backlight/bl_power"
                logger.debug("Turning display power on")
                # subprocess.check_output(a, shell=True)
                cls._backlight.power = True
        else:
            pass
        cls._backlight_state = 1
        cls._display_lock.release()
        logger.debug("Display turned on")

    @classmethod
    def turn_display_off(cls):
        cls._display_lock.acquire()
        if DisplayController.is_raspberry_pi():
            if DisplayController.is_hdmi_display():
                subprocess.run(["vcgencmd", "display_power", "0"])
            elif DisplayController.is_raspberry_pi():
                # rpi 7" touchscreen
                # a = "echo 1 | sudo tee /sys/class/backlight/rpi_backlight/bl_power"
                logger.debug("Turning display power off")
                # subprocess.check_output(a, shell=True)
                cls._backlight.power = False
        else:
            pass
        cls._backlight_state = 0
        cls._display_lock.release()
        logger.debug("Display turned off")

    @classmethod
    def set_display_backlight(cls, brightness):
        cls._display_lock.acquire()
        if DisplayController.is_raspberry_pi():
            if DisplayController.is_hdmi_display():
                pass
            elif DisplayController.is_raspberry_pi():
                # rpi 7" touchscreen
                # a = "echo {0} | sudo tee /sys/class/backlight/rpi_backlight/brightness".format(brightness)
                logger.debug("Setting display brightness")
                # subprocess.check_output(a, shell=True)
                cls.brightness = int(brightness)
        else:
            pass
        cls._display_lock.release()
        logger.debug("Display backlight brightness set")
