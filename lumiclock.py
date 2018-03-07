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
from functools import partial
from animated_gif_label import AnimatedGIFLabel


class LumiClockApplication(tk.Frame):
    """
    Main window of the application
    """
    def __init__(self, master=None):
        tk.Frame.__init__(self, master, bg='black')
        self.last_time = ""
        self.master = master
        self.toggle_ampm = True

        # Screen dimensions
        self.screen_width = self.master.winfo_screenwidth()
        self.screen_height = self.master.winfo_screenheight()
        geo = "{0}x{1}".format(int(800), int(self.screen_height / 2))
        self.master.geometry(geo)
        self.master["bg"] = 'black'

        # Gets rid of title bar, but OS window decorations remain
        # self.master.overrideredirect(True)
        self.grid()
        #self.columnconfigure(0, minsize=int(self.screen_width / 20))
        #self.columnconfigure(1, minsize=int(self.screen_width / 10))
        self.rowconfigure(0, minsize=int(self.screen_height / 2))
        self._createWidgets()

        # Set up escape key as full screen toggle
        self.fullscreen = True
        self.master.bind("<Escape>", self._toggle_fullscreen)
        self._toggle_fullscreen()
        #self.master.attributes("-fullscreen", self.fullscreen)
        # self.master.wm_attributes('-fullscreen', self.fullscreen)

        # Capture left mouse double clicks anywhere in the Frame
        self.master.bind("<Double-Button-1>", self.quit_app)
        # Capture right mouse clicks
        # self.master.bind("<Button-2>", self._click_handler)

        self.context_menu = ContextMenu(self)

        # Capture left mouse single click anywhere in the Frame
        self.master.bind("<Button-1>", self._show_context_menu)

    def _show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def _toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen  # Just toggling the boolean
        self.master.attributes("-fullscreen", self.fullscreen)
        return "break"

    def _click_handler(self, event):
        self.label["text"] = "clicked at {0} {1}".format(event.x, event.y)

    def quit_app(self, event):
        self.quit()

    def _createWidgets(self):
        r = 0

        # Try out fonts and in a label

        #self.clockfont = tkfont.Font(family='Helvetica', size=72*3)
        #self.clockfont = tkfont.Font(family='readoutcondensed', size=72*3, weight='bold')
        self.clockfont = tkfont.Font(family='Digital-7 Mono', size=72*3)
        print (self.clockfont.actual())
        print (self.clockfont.metrics())

        # Sets the label text (the clock) statically
        # Hunt for a color...
        self.textbox = tk.Label(self, text="12:00", font=self.clockfont, fg="#EC3818", bg='black')
        self.textbox.grid(row=r, column=0)

        # image display
        # animated GIF
        self.image_label = AnimatedGIFLabel(bg='black')
        self.image_label.grid(row=r, column=1, sticky=tk.W+tk.N+tk.S)
        # http://www.chimply.com/Generator#classic-spinner,animatedTriangles
        # TODO Better way to select default spinner
        self.image_label.load("spiral_triangles.gif")
        # self.image_label.delay = 160

        r += 1

        self.label = tk.Label(self, text="Quit label:", bg="#EC3818")
        self.label.grid(row=r, column=0, sticky=tk.W)
        self.quitButton = tk.Button(self, bg="#ec3818", text='Quit', command=self.quit)
        self.quitButton.grid(row=r, column=1, sticky=tk.E+tk.W, pady=0)

        # Start the clock
        self._update_clock()

    def _update_clock(self):
        #current = datetime.datetime.now().strftime("%I:%M")
        now = datetime.datetime.now()
        # current = now.strftime("%I:%M %p")
        current = now.strftime("%I:%M")
        if now.hour >= 12:
            current += "."
        else:
            current += " "
        self.toggle_ampm = not self.toggle_ampm
        if current[0] == '0':
            current = " " + current[1:]
        if self.last_time != current:
            # How to change the label in code
            self.textbox["text"] = current
            self.last_time = current

        self.after(1000, self._update_clock)

    def change_spinner(self, gif):
        print(gif)
        self.image_label.unload()
        self.image_label.load(gif)

class ContextMenu(tk.Menu):
    """
    Context menu for allowing user to choose spinner
    """
    def __init__(self, parent, **args):
        tk.Menu.__init__(self, **args)
        self.parent = parent

        # Create a context menu item for each available GIF
        gifs = glob.glob("*.gif")
        for g in gifs:
            # This is the best way I could find to pass the GIF name to the handler
            self.add_command(label=g, command=partial(self._new_spinner, g))

        self.add_command(label="Quit", command=self._quit)

    def _new_spinner(self, gif):
        # Change the current spinner to the newly selected GIF
        self.parent.change_spinner(gif)

    def _quit(self):
        """
        Quit app
        :return:
        """
        self.parent.quit_app(None)


if __name__ == '__main__':
    root = tk.Tk()
    app = LumiClockApplication(master=root)
    app.master.title('LumiClock')
    app.mainloop()
