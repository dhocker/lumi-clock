#
# Raspberry Pi display controller
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

import threading
import subprocess
import platform
from app_logger import AppLogger

# Logger init
the_app_logger = AppLogger("lumiclock")
logger = the_app_logger.getAppLogger()


class DisplayController():
    """
    The display is controlled by a state machine.
    Display off
    Display on
    Count down to display off
    Unknown

    """

    # states
    _state_display_off = 0
    _state_display_on = 1
    _state_display_count_down = 2
    _state_unknown = -1

    # Serializes access to the display
    _display_lock = threading.Lock()
    _backlight_state = 0

    def __init__(self, count_down_time=60*1):
        """
        Class constructor.
        count_down_time: in seconds, how long to wait before entering the
            display off state.
        """
        self._display_state = self._state_unknown
        self._count_down_time = count_down_time

        # Public properties
        self.down_counter = 0
        self.sensor_value = 0

    """
    The techniques used to manage diffrent displays was
    found at: https://scribles.net/controlling-display-backlight-on-raspberry-pi/
    """
    
    def set_display_state(self, sensor_value):
        self.sensor_value = sensor_value
        if self._display_state == self._state_display_off:
            if self.sensor_value:
                # new state is on
                self._display_state = self._state_display_on
                self.display_on()
        elif self._display_state == self._state_display_on:
            if not self.sensor_value:
                # New state is counting down
                self.down_counter = self._count_down_time
                self._display_state = self._state_display_count_down
                self.display_count_down()
        elif self._display_state == self._state_display_count_down:
            # Counting down to display off
            self.down_counter -= 1
            if self.down_counter <= 0:
                # New state is display off
                self._display_state = self._state_display_off
                self.display_off()
            elif self.sensor_value:
                # New state is display on
                self._display_state = self._state_display_on
                self.display_on()
            else:
                # Maintain same state
                self.display_counting_down()
        elif self._display_state == self._state_unknown:
            if self.sensor_value:
                self._display_state = self._state_display_on
                self.display_on()
            else:
                self.down_counter = self._count_down_time
                self._display_state = self._state_display_count_down
                self.display_count_down()
        else:
            # Unknown state
            logger.debug("Undefined state", self._display_state)

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
        # A weak test for the RPi since it declares any ARM based system is an RPi.
        return platform.machine().startswith("arm")

    """
    These methods can be overriden in a derived class
    to provide advanced customization of each state.
    Each method is called when the state is entered.
    """

    def display_on(self):
        self.turn_display_on()

    def display_off(self):
        self.turn_display_off()

    def display_count_down(self):
        logger.debug("Starting count down to display off from %d", self.down_counter)

    def display_counting_down(self):
        if (self.down_counter % 30) == 0:
            logger.debug("Counting down to display off %d", self.down_counter)

    """
    The techniques used to manage diffrent displays was
    found at: https://scribles.net/controlling-display-backlight-on-raspberry-pi/
    Note that these are class methods because there is only one physical display.
    """

    @classmethod
    def turn_display_on(cls):
        cls._display_lock.acquire()
        if DisplayController.is_raspberry_pi():
            if DisplayController.is_hdmi_display():
                subprocess.run(["vcgencmd", "display_power", "1"])
            else:
                # rpi 7" touchscreen
                a = "echo 0 | sudo tee /sys/class/backlight/rpi_backlight/bl_power"
                logger.debug(a)
                subprocess.check_output(a, shell=True)
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
                a = "echo 1 | sudo tee /sys/class/backlight/rpi_backlight/bl_power"
                logger.debug(a)
                subprocess.check_output(a, shell=True)
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
                a = "echo %d | sudo tee /sys/class/backlight/rpi_backlight/brightness".format(brightness)
                logger.debug(a)
                subprocess.check_output(a, shell=True)
        else:
            pass
        cls._display_lock.release()
        logger.debug("Display backlight brightness set")
