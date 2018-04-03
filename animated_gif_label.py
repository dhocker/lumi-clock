#
# A label that displays images, and plays them if they are GIFs
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
from PIL import Image, ImageTk
from itertools import count
from app_logger import AppLogger


# Logger init
the_app_logger = AppLogger("lumiclock")
logger = the_app_logger.getAppLogger()


class AnimatedGIFLabel(tk.Label):
    """
        a label that displays images, and plays them if they are GIFs
        Adapted from the following SO article
        https://stackoverflow.com/questions/43770847/play-an-animated-gif-in-python-with-tkinter
    """
    def __init__(self, parent, **args):
        tk.Label.__init__(self, parent, **args)
        self.loc = 0
        self.im = None
        self.frames = []
        self.delay = 100
        self.config(pady=0)
        self.running = False

    def load(self, im, delay=None):
        """
        Load an animated GIF
        :param im: An image instance or the name of a GIF file.
        :param delay: Override for delay duration.
        :return:
        """
        self.im = im
        if isinstance(im, str):
            im = Image.open(im)

        self.frames = []
        self.loc = 0

        try:
            for i in count(1):
                self.frames.append(ImageTk.PhotoImage(im.copy()))
                im.seek(i)
        except EOFError:
            pass
        logger.debug("%d frames in GIF %s", len(self.frames), im)

        if not delay:
            try:
                self.delay = im.info['duration']
                logger.debug("GIF duration: %d", self.delay)
            except:
                self.delay = 100
        else:
            self.delay = delay
        logger.debug("Delay: %d", self.delay)

        if len(self.frames) == 1:
            self.config(image=self.frames[0])
        elif not self.running:
            # Only once!
            self._next_frame()
            self.running = True

    def unload(self):
        """
        Remove the current GIF
        :return:
        """
        self.config(image=None)
        self.frames = None

    def _next_frame(self):
        """
        Display the next frame of the animated GIF
        :return:
        """
        if self.frames:
            self.loc += 1
            self.loc %= len(self.frames)
            self.config(image=self.frames[self.loc])
            self.after(self.delay, self._next_frame)
        else:
            self.running = False
