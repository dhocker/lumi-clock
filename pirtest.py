# -*- coding: UTF-8 -*-
#
# PIR sensor testing
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

import RPi.GPIO as GPIO
import time
import datetime
from app_logger import AppLogger

# Logger init
the_app_logger = AppLogger("lumiclock")
logger = the_app_logger.getAppLogger()

def old_main():
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

def pir_update_handler(sensor_value):
    # NOTE that this function is called on the sensor thread, NOT the main thread
    now = datetime.datetime.now()
    print(now.strftime("%H:%M:%S"), sensor_value)


def main():
    pir = 12
    from pir_sensor_thread import SensorThread
    threadinst = SensorThread(notify=pir_update_handler, pir_pin=12, time_off=10, time_on=10)
    threadinst.start()

    try:
        while True:
            time.sleep(1.0)
    except:
        print()
        print("Keyboard interrupt")

    threadinst.terminate()
    the_app_logger.Shutdown()

    print("End")


if __name__ == '__main__':
    main()
