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
from tkinter import font as tkfont
import datetime
import glob
import sys
from functools import partial
from animated_gif_label import AnimatedGIFLabel
from configuration import QConfiguration
from app_logger import AppLogger


# Logger init
the_app_logger = AppLogger("lumiclock")
logger = the_app_logger.getAppLogger()


class LumiClockApplication(tk.Frame):
    """
    Main window of the application
    """
    def __init__(self, master=None):
        tk.Frame.__init__(self, master, bg='black')
        self.last_time = ""
        self.master = master
        self.toggle_ampm = True
        self.fullscreen = False
        self.run_clock = False

        # Screen dimensions
        self.screen_width = self.master.winfo_screenwidth()
        self.screen_height = self.master.winfo_screenheight()
        logger.debug("%d x %d", self.screen_width, self.screen_height)
        geo = "{0}x{1}-0-10".format(self.screen_width, self.screen_height)
        logger.debug("Geometry: %s", geo)
        self.master.geometry(geo)
        self.master["bg"] = 'black'

        # Font size in pixels
        self.font_size = -int((self.screen_height) * 0.45)

        # This trick hides the cursor
        self.master.config(cursor="none")

        # Gets rid of title bar, but OS window decorations remain
        # self.master.overrideredirect(True)
        self.pack(fill=tk.BOTH, expand=1)

        self._createWidgets()

        # Set up escape key as full screen toggle
        self.master.bind("<Escape>", self.toggle_fullscreen)

        # This show set the display to full screen
        self.toggle_fullscreen()

        self.context_menu = ContextMenu(self)

        # Capture left mouse single click anywhere in the Frame
        self.bind("<Button-1>", self._show_context_menu)

    def _show_context_menu(self, event):
        # self.context_menu.post(event.x_root, event.y_root)
        self.context_menu.post(event.x_root, 0)

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
        r = 0
        # Font size needs to be in config
        self.clockfont = tkfont.Font(family=QConfiguration.font, size=self.font_size)
        logger.debug(self.clockfont.actual())
        logger.debug(self.clockfont.metrics())

        # Sets the label text (the clock) statically
        self.textbox = tk.Label(self, text="12:00", font=self.clockfont, fg=QConfiguration.color, bg='black')
        self.textbox.place(x=0, rely=0.25, height=-self.font_size)
        self.textbox.bind("<Button-1>", self._show_context_menu)

        # image display
        # animated GIF
        self.image_label = AnimatedGIFLabel(self, bg='black')
        # http://www.chimply.com/Generator#classic-spinner,animatedTriangles
        # Select default spinner
        self.image_label.load(QConfiguration.spinner)
        self.image_label.place(relx=1, x=-self.image_label.width, rely=0.5, anchor=tk.CENTER)
        self.image_label.bind("<Button-1>", self._show_context_menu)
        # Start the clock
        self.run_clock = True
        self._update_clock()

    def _update_clock(self):
        """
        Run the clock unless we are in the process of quiting
        :return:
        """
        if self.run_clock:
            now = datetime.datetime.now()
            current = now.strftime("%I:%M")
            if now.hour >= 12:
                current += "."
            else:
                current += " "
            self.toggle_ampm = not self.toggle_ampm
            if current[0] == '0':
                current = " " + current[1:]
            # HACK to space clock digits and spinner
            # if self.fullscreen:
            #     current += " "
            if self.last_time != current:
                # How to change the label in code
                self.textbox["text"] = current
                self.last_time = current

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
        self.clockfont = tkfont.Font(family=font_name, size=self.font_size)
        self.textbox.config(font=self.clockfont)
        logger.debug("Font changed: %s", font_name)

class SpinnerMenu(tk.Menu):
    """
    Menu containing a list of all available spinner GIFs
    """
    def __init__(self, parent, command=None, **args):
        """

        :param parent: Parent of this menu
        :param command: Callback when a spinner GIF is selected.
        :param args:
        """
        tk.Menu.__init__(self, parent, **args)
        self.parent = parent

        # Create a context menu item for each available GIF
        gifs = glob.glob("*.gif")
        gifs.sort()
        for g in gifs:
            # This is the best way I could find to pass the GIF name to the handler
            self.add_command(label=g, command=partial(command, g))


class FontMenu(tk.Menu):
    """
    Menu containing a list of all available fonts
    """
    def __init__(self, parent, command=None, **args):
        """

        :param parent:
        :param command: Callback when a font is selected
        :param args:
        """
        tk.Menu.__init__(self, parent, **args)
        self.parent = parent

        fonts = list(tkfont.families())
        fonts.sort()
        for item in fonts:
            self.add_command(label=item, command=partial(command, item))

class ContextMenu(tk.Menu):
    """
    Context menu for allowing user to interact with the clock
    """
    def __init__(self, parent, tearoff=0, **args):
        tk.Menu.__init__(self, parent, tearoff=tearoff, **args)
        self.parent = parent

        self.spinner_menu = SpinnerMenu(self, command=self._new_spinner)
        self.add_cascade(label="Spinners", menu=self.spinner_menu)

        self.font_menu = FontMenu(self, command=self._new_font)
        self.add_cascade(label="Fonts", menu=self.font_menu)

        self.add_separator()
        self.add_command(label="Toggle fullscreen", command=self._toggle_fullscreen)
        self.add_separator()
        self.add_command(label="Save configuration", command=QConfiguration.save)
        self.add_separator()
        self.add_command(label="Quit", command=self._quit)

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

    def _quit(self):
        """
        Quit app
        :return:
        """
        self.destroy()
        self.parent.quit_app(None)


if __name__ == '__main__':
    # Start the PIR sensor monitor
    if QConfiguration.pirsensor:
        from pir_sensor_thread import SensorThread
        threadinst = SensorThread(count_down_time=QConfiguration.timeout * 60)
        threadinst.start()
    
    # Create main window and run the event loop
    root = tk.Tk()
    app = LumiClockApplication(master=root)
    app.master.title('LumiClock')
    app.mainloop()

    # Terminate sensor monitor
    if QConfiguration.pirsensor:
        threadinst.terminate()
