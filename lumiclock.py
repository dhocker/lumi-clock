#
# Digital clock inspired by the LumiTime clock series
# Copyright (C) 2018  Dave Hocker (email: athomex10@gmail.com)
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


import tkinter as tk # In python2 it's Tkinter
from tkinter import font as tkfont, messagebox
import datetime
import glob
from functools import partial
import os
from lumiclock_app import LumiClockApplication
from animated_gif_label import AnimatedGIFLabel
from configuration import QConfiguration
from app_logger import AppLogger


# Logger init
the_app_logger = AppLogger("lumiclock")
logger = the_app_logger.getAppLogger()


def main():
    # Start the PIR sensor monitor
    threadinst = None
    if QConfiguration.pirsensor:
        from pir_sensor_thread import SensorThread
        threadinst = SensorThread(count_down_time=QConfiguration.timeout * 60)
        threadinst.start()

    # Create main window and run the event loop
    root = tk.Tk()
    app = LumiClockApplication(master=root, sensor=threadinst)
    root.title('LumiClock')

    # Set up icon
    try:
        if os.name == "posix":
            # Linux or OS X
            root.iconbitmap("lumiclock.xbm")
            logger.debug("Loaded icon lumiclock.xbm")
        elif os.name == "nt":
            # Windows
            root.iconbitmap("lumiclock.ico")
            logger.debug("Loaded icon lumiclock.ico")
    except Exception as ex:
        logger.error(str(ex))

    root.mainloop()

    # Terminate sensor monitor
    if QConfiguration.pirsensor:
        threadinst.terminate()


if __name__ == '__main__':
    main()
