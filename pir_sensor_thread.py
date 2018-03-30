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

class SensorThread(threading.Thread):
    """
    Thread based class for working with the Adafruit PIR sensor.
    This class can be used as-is or it can be used as the base
    class for a more customized implementation.
    Reference: http://adafruit/189
    
    The PIR sensor is monitored by a state machine.
    Display off
    Display on
    Count down to display off
    Unknown
    
    The initial state is unknown.
    """
    def __init__(self, pir_pin=12, count_down_time=60*1, name="PIRSensorThread"):
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

        # states
        self.state_display_off = 0
        self.state_display_on = 1
        self.state_display_count_down = 2
        self.state_unknown = -1
        self.display_state = self.state_unknown

        self.count_down_time = count_down_time
        self.down_counter = 0
        self.terminate_thread = False
    
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
        self.terminate_thread = True
        self.join()

    def run_sensor(self):
        """
        Monitors the PIR sensor. Expects to be called on
        its own thread.
        """

        while not self.terminate_thread:
            # Read the current state of the PIR sensor.
            # 0 = no movement detected
            # 1 = movement detected
            v = GPIO.input(self.pir_pin)
            
            if self.display_state == self.state_display_off:
                if v:
                    # new state is on
                    self.display_state = self.state_display_on
                    self.display_on()
            elif self.display_state == self.state_display_on:
                if not v:
                    # New state is counting down
                    self.down_counter = self.count_down_time
                    self.display_state = self.state_display_count_down
                    self.display_count_down()
            elif self.display_state == self.state_display_count_down:
                # Counting down to display off
                self.down_counter -= 1
                if self.down_counter <= 0:
                    # New state is display off
                    self.display_state = self.state_display_off
                    self.display_off()
                elif v:
                    # New state is display on
                    self.display_state = self.state_display_on
                    self.display_on()
                else:
                    # Maintain same state
                    pass
            elif self.display_state == self.state_unknown:
                if v:
                    self.display_state = self.state_display_on
                    self.display_on()
                else:                    
                    self.down_counter = self.count_down_time
                    self.display_state = self.state_display_count_down
                    self.display_count_down()
            else:
                # Unknown state
                print("Undefined state", self.display_state)
            
            print("v:", v, "state:", self.display_state, "count:", self.down_counter)
            # This is why the sensor monitor runs on its own thread.
            time.sleep(1.0)
        print("Sensor thread terminated")

    @staticmethod
    def is_hdmi_display():
        """
        Answers the question: Is the current display HDMI?
        Otherwise, it is assumed to be the RPi 7" touchscreen.
        """
        res = subprocess.run(["tvservice", "-s"], stdout=subprocess.PIPE)
        res = str(res.stdout, 'utf-8')
        if res.find("HDMI") != -1:
            return True
        return False
    
    """
    These methods can be overriden in a derived class
    to provide advanced customization of each state.
    Each method is called when the state is entered.
    The techniques used to manage diffrent displays was
    found at: https://scribles.net/controlling-display-backlight-on-raspberry-pi/
    """
    
    def display_on(self):
        print("Display on")
        if SensorThread.is_hdmi_display():
            subprocess.run(["vcgencmd", "display_power", "1"])
        else:
            # rpi 7" touchscreen
            a = ["echo", "0", "|", "sudo", "tee", "/sys/class/backlight/rpi_backlight/bl_power"]
            subprocess.check_output(a, shell=True)
            
    def display_off(self):
        print("Display off")
        if SensorThread.is_hdmi_display():
            subprocess.run(["vcgencmd", "display_power", "0"])
        else:
            # rpi 7" touchscreen
            a = ["echo", "1", "|", "sudo", "tee", "/sys/class/backlight/rpi_backlight/bl_power"]
            subprocess.check_output(a, shell=True)
    
    def display_count_down(self):
        print("Counting down to display off from", self.down_counter)
