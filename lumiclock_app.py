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
from animated_gif_label import AnimatedGIFLabel
from configuration import QConfiguration
from display_controller import DisplayController
from app_logger import AppLogger


# Logger init
the_app_logger = AppLogger("lumiclock")
logger = the_app_logger.getAppLogger()


class LumiClockApplication(tk.Frame):
    """
    Main window of the application. Designed to be a singleton.
    """
    def __init__(self, master=None, sensor=None, display=None):
        tk.Frame.__init__(self, master, bg='black')
        self._sensor = sensor
        self._display = display
        self.last_time = ""
        self.master = master
        self.toggle_ampm = True
        self.fullscreen = False
        self.run_clock = False

        # Screen dimensions
        self.screen_width = self.master.winfo_screenwidth()
        self.screen_height = self.master.winfo_screenheight()
        logger.debug("%d x %d", self.screen_width, self.screen_height)
        geo = "{0}x{1}".format(self.screen_width, self.screen_height)
        logger.debug("Geometry: %s", geo)
        self.master.geometry(geo)
        self.master["bg"] = 'black'

        # Set display brightness on RPi
        DisplayController.set_display_backlight(QConfiguration.backlight)

        # Font size in pixels
        if QConfiguration.fontsize:
            self.font_size = QConfiguration.fontsize
        else:
            # Default to 45% of screen height
            self.font_size = int(0.45 * self.screen_height)

        # This trick hides the cursor
        self.master.config(cursor="none")

        # Fill the whole window
        self.pack(fill=tk.BOTH, expand=1)

        self._createWidgets()

        # Set up escape key as full screen toggle
        self.master.bind("<Escape>", self.toggle_fullscreen)

        # This show set the display to full screen
        self.toggle_fullscreen()

        self.context_menu = ContextMenu(self, height=self.screen_height)

        # Capture left mouse single click anywhere in the Frame
        self.bind("<Button-1>", self._show_context_menu)

    def _show_context_menu(self, event):
        # Always position context menu at the top so there is maximum
        # amount of screen for submenus.
        self.context_menu.post(event.x_root, 0)
        return "break"

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen  # Just toggling the boolean
        self.master.attributes("-fullscreen", self.fullscreen)
        return "break"

    def quit_app(self, event):
        self.run_clock = False
        self.master.destroy()

    def _createWidgets(self):
        """
        Create clock and spinner widgets
        :return:
        """
        # Define the clock widget and its font
        self.textbox = tk.Label(self, text="12:00", fg=QConfiguration.color, bg='black')
        self.change_font(QConfiguration.font)
        self.textbox.bind("<Button-1>", self._show_context_menu)

        # image display
        # animated GIF
        self.image_label = AnimatedGIFLabel(self, bg='black')
        # http://www.chimply.com/Generator#classic-spinner,animatedTriangles
        # Select default spinner
        self.image_label.load(QConfiguration.spinner)
        self.image_label.place(relx=1, x=-self.image_label.width, rely=0.5, anchor=tk.CENTER)
        self.image_label.bind("<Button-1>", self._show_context_menu)

        # One line debug display at the bottom of the display
        self.debugfont = tkfont.Font(family='Helvetica', size=-20)
        self.debug_display = tk.Label(self, text="", font=self.debugfont,
                                      fg=QConfiguration.color, bg='black')
        self.debug_display.place(x=10, rely=1.0, y=self.debugfont['size']-10)

        # Start the clock
        self.run_clock = True
        self._update_clock()

    def _update_clock(self):
        """
        Run the clock unless we are in the process of quiting
        :return:
        """
        if self.run_clock:
            # Update the time display
            now = datetime.datetime.now()
            current = now.strftime("%I:%M")
            if now.hour >= 12:
                if (now.second % 2) == 0:
                    current += "."
                else:
                    current += " "
            else:
                current += " "
            self.toggle_ampm = not self.toggle_ampm
            if current[0] == '0':
                current = current[1:]
            if self.last_time != current:
                # How to change the label in code
                self.textbox["text"] = current
                self.last_time = current

            # Update debug display
            dd = ""
            if QConfiguration.debugdisplay:
                dd = "Time: {0}".format(now.strftime("%Y-%m-%d %H:%M:%S"))
                if self._sensor:
                    dd += " | PIR Sensor: {0}".format(self._sensor.sensor_value)
                    dd += " | Count Down: {0}".format(self._display.down_counter)
            self.debug_display["text"] = dd

            self.after(1000, self._update_clock)

    def change_spinner(self, gif):
        """
        Change to a new spinner GIF
        :param gif:
        :return:
        """
        self.image_label.unload()
        self.image_label.load(gif)
        logger.debug("Spinner changed: %s", gif)

    def change_font(self, font_name):
        """
        Change the current clock font. Reposition the clock widget
        so it appears to be visually centered.
        :param font_name: The new font family.
        :return: None.
        """
        self.clockfont = tkfont.Font(family=font_name, size=self.font_size)
        self.textbox.config(font=self.clockfont)

        # Pick the largest of the size and linespace in an effort to keep
        # the y offset small.
        # The Digital 7 fonts have negative descent values. This throws
        # positioning out of whack. To compensate, the absolute values
        # for ascent and descent are used to calculate the practical linespace.
        linespace = abs(self.clockfont.metrics()["ascent"]) + abs(self.clockfont.metrics()["descent"])
        actual_size = max(self.clockfont.actual()["size"], linespace)
        self.textbox.place(x=0, y=int((self.screen_height - actual_size) / 2), height=actual_size)

        logger.debug("Font changed to: %s", font_name)
        logger.debug(self.clockfont.actual())
        logger.debug(self.clockfont.metrics())
        logger.debug("Configured font size: %d", self.font_size)
        logger.debug("Calculated linespace: %d", linespace)
        logger.debug("Clock widget y = %d", int((self.screen_height - actual_size) / 2))

    def larger_font(self):
        font_name = self.clockfont.actual()["family"]
        self.font_size = int(self.font_size * 1.1)
        self.change_font(font_name)
        return self.font_size

    def smaller_font(self):
        font_name = self.clockfont.actual()["family"]
        self.font_size = int(self.font_size * 0.9)
        self.change_font(font_name)
        return self.font_size


class SpinnerMenu(tk.Menu):
    """
    Menu containing a list of all available spinner GIFs
    """
    def __init__(self, parent, command=None, height=20, **args):
        """

        :param parent: Parent of this menu
        :param command: Callback when a spinner GIF is selected.
        :param args:
        """
        tk.Menu.__init__(self, parent, tearoff=0, **args)
        self.parent = parent

        menu_font = tkfont.Font(family="", size=11)
        line_height = menu_font.metrics("linespace") + menu_font.metrics("ascent") + menu_font.metrics("descent")
        max_menu_count = int(height / line_height)

        # Create a context menu item for each available GIF
        gifs = glob.glob("*.gif")
        gifs.sort()
        for g in gifs:
            # This is the best way I could find to pass the GIF name to the handler
            self.add_command(label=g, font=menu_font, command=partial(command, g))


class FontMenu(tk.Menu):
    """
    Menu containing a list of all available fonts
    """
    def __init__(self, parent, command=None, height=20, **args):
        """

        :param parent:
        :param command: Callback when a font is selected
        :param args:
        """
        tk.Menu.__init__(self, parent, tearoff=0, **args)
        self.parent = parent

        menu_font = tkfont.Font(family="", size=11)
        line_height = menu_font.metrics("linespace") + menu_font.metrics("ascent") + menu_font.metrics("descent")
        max_menu_count = int(height / line_height)

        fonts = list(tkfont.families())
        fonts.sort()
        count = max_menu_count
        for item in fonts:
            if count <= 0:
                self.add_command(label=item, font=menu_font, command=partial(command, item), columnbreak=True)
                count = max_menu_count
            else:
                self.add_command(label=item, font=menu_font, command=partial(command, item))
            count -= 1

class ContextMenu(tk.Menu):
    """
    Context menu for allowing user to interact with the clock
    """
    def __init__(self, parent, tearoff=0, height=20, **args):
        tk.Menu.__init__(self, parent, tearoff=tearoff, **args)
        self.parent = parent
        menu_font = tkfont.Font(family="", size=11)

        self.spinner_menu = SpinnerMenu(self, height=height, command=self._new_spinner)
        self.add_cascade(label="Spinners", menu=self.spinner_menu, font=menu_font)

        self.add_separator()
        self.font_menu = FontMenu(self, command=self._new_font, height=height)
        self.add_cascade(label="Fonts", menu=self.font_menu, font=menu_font)
        self.add_command(label="Larger", command=self._larger_font, font=menu_font)
        self.add_command(label="Smaller", command=self._smaller_font, font=menu_font)

        self.add_separator()
        self.add_command(label="Toggle fullscreen", command=self._toggle_fullscreen, font=menu_font)
        self.add_separator()
        self.add_command(label="Toggle Debug display", command=self._toggle_debug_display, font=menu_font)
        self.add_separator()
        self.add_command(label="Save configuration", command=self._save_configuration, font=menu_font)
        self.add_separator()
        self.add_command(label="Quit", command=self._quit, font=menu_font)

    def _toggle_fullscreen(self):
        """
        Toggle screen between fullscreen and window
        :return:
        """
        self.parent.toggle_fullscreen()

    def _new_spinner(self, gif):
        """
        Change the current spinner to the newly selected GIF
        :param gif:
        :return:
        """
        self.parent.change_spinner(gif)
        QConfiguration.spinner = gif

    def _new_font(self, font_name):
        self.parent.change_font(font_name)
        QConfiguration.font = font_name

    def _larger_font(self):
        QConfiguration.fontsize = self.parent.larger_font()

    def _smaller_font(self):
        QConfiguration.fontsize = self.parent.smaller_font()

    def _save_configuration(self):
        QConfiguration.save()
        messagebox.showinfo("Save Configuration", "The current configuration has been saved")

    def _toggle_debug_display(self):
        QConfiguration.debugdisplay = not QConfiguration.debugdisplay

    def _quit(self):
        """
        Quit app
        :return:
        """
        self.destroy()
        self.parent.quit_app(None)
