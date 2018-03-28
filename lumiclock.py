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
# TODO Need some sort of configuration file to define default behavior
#   Default GIF
#   Default font
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
        self.fullscreen = True
        self.run_clock = False

        # Screen dimensions
        self.screen_width = self.master.winfo_screenwidth()
        self.screen_height = self.master.winfo_screenheight()
        logger.debug("%d x %d", self.screen_width, self.screen_height)
        geo = "{0}x{1}".format(int(1000), int(self.screen_height / 2))
        self.master.geometry(geo)
        self.master["bg"] = 'black'

        # Gets rid of title bar, but OS window decorations remain
        # self.master.overrideredirect(True)
        self.grid()
        self.rowconfigure(0, minsize=int(self.screen_height / 2))

        self._createWidgets()

        # Set up escape key as full screen toggle
        self.master.bind("<Escape>", self.toggle_fullscreen)
        self.toggle_fullscreen()

        # Capture left mouse double clicks anywhere in the Frame
        self.master.bind("<Double-Button-1>", self.quit_app)
        # The right mouse button is OS dependendent
        # Capture right mouse clicks
        if sys.platform.startswith('darwin'):
            # On macOS button 2 is the right button
            self.master.bind("<Button-2>", self._click_handler)
        else:
            # On other systems button 3 is the right button
            self.master.bind("<Button-3>", self._click_handler)

        self.context_menu = ContextMenu(self)

        # Capture left mouse single click anywhere in the Frame
        self.bind("<Button-1>", self._show_context_menu)

    def _show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen  # Just toggling the boolean
        self.master.attributes("-fullscreen", self.fullscreen)
        # Adjust row height for effective size of window
        # The goal is to get the clock vertically centered
        if self.fullscreen:
            self.rowconfigure(0, minsize=int(self.screen_height))
        else:
            self.rowconfigure(0, minsize=int(self.screen_height / 2))
        self._update_clock()
        return "break"

    def _click_handler(self, event):
        self.label["text"] = "clicked at {0} {1}".format(event.x, event.y)

    def quit_app(self, event):
        self.run_clock = False
        self.master.destroy()
        sys.exit(0)

    def _createWidgets(self):
        """
        Create clock and spinner widgets
        :return:
        """
        r = 0

        self.clockfont = tkfont.Font(family=QConfiguration.font, size=72*3)
        logger.debug(self.clockfont.actual())
        logger.debug(self.clockfont.metrics())

        # Sets the label text (the clock) statically
        self.textbox = tk.Label(self, text="12:00", font=self.clockfont, fg=QConfiguration.color, bg='black')
        self.textbox.grid(row=r, column=0, sticky=tk.W+tk.N+tk.S)
        self.textbox.bind("<Button-1>", self._show_context_menu)

        # image display
        # animated GIF
        self.image_label = AnimatedGIFLabel(bg='black')
        self.image_label.grid(row=r, column=1, sticky=tk.E+tk.N+tk.S)
        self.image_label.bind("<Button-1>", self._show_context_menu)
        # http://www.chimply.com/Generator#classic-spinner,animatedTriangles
        # Select default spinner
        self.image_label.load(QConfiguration.spinner)

        r += 1

        self.label = tk.Label(self, text="Quit label:", bg=QConfiguration.color)
        self.label.grid(row=r, column=0, sticky=tk.W)
        self.quitButton = tk.Button(self, bg=QConfiguration.color, text='Quit', command=self.quit)
        self.quitButton.grid(row=r, column=1, sticky=tk.E+tk.W, pady=0)

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
            if self.fullscreen:
                current += " "
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
        print(gif)
        self.image_label.unload()
        self.image_label.load(gif)

class ContextMenu(tk.Menu):
    """
    Context menu for allowing user to interact with the clock
    """
    def __init__(self, parent, **args):
        tk.Menu.__init__(self, **args)
        self.parent = parent

        # Create a context menu item for each available GIF
        gifs = glob.glob("*.gif")
        for g in gifs:
            # This is the best way I could find to pass the GIF name to the handler
            self.add_command(label=g, command=partial(self._new_spinner, g))

        self.add_separator()
        self.add_command(label="Toggle fullscreen", command=self._toggle_fullscreen)
        self.add_command(label="Save configuration", command=QConfiguration.save)
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

    def _quit(self):
        """
        Quit app
        :return:
        """
        self.destroy()
        self.parent.quit_app(None)


if __name__ == '__main__':
    root = tk.Tk()
    app = LumiClockApplication(master=root)
    app.master.title('LumiClock')
    app.mainloop()
