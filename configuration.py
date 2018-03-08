#
# LumiClock application configuration
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
import os
import os.path
import inspect
import json
from app_logger import AppLogger


# Logger init
the_app_logger = AppLogger("lumiclock")
logger = the_app_logger.getAppLogger()


class QConfiguration:
    """
    Encapsulates configuration data
    """
    macOS = False
    file_path = ""
    full_file_path = ""
    font = "Courier New"
    spinner = "spiral_triangles.gif"
    color = "#EC3818"
    loglevel = "debug"
    cwd = ""
    conf_exists = False

    @classmethod
    def load(cls):
        """
        Load credentials from configuration file. The location of the iex.conf
        file is OS dependent. The permissions of the iex.conf file should allow
        access ONLY by the user.
        :return: None
        """
        file_name = "lumiclock.conf"
        if os.name == "posix":
            # Linux or OS X
            cls.file_path = "{0}/lumiclock/".format(os.environ["HOME"])
            cls.macOS = (os.uname()[0] == "Darwin")
        elif os.name == "nt":
            # Windows
            cls.file_path = "{0}\\lumiclock\\".format(os.environ["APPDATALOCAL"])
        cls.full_file_path = cls.file_path + file_name

        # Read conf file
        try:
            cf = open(cls.full_file_path, "r")
            cfj = json.loads(cf.read())
            if "loglevel" in cfj:
                cls.loglevel = cfj["loglevel"]
            if "font" in cfj:
                cls.font = cfj["font"]
            if "spinner" in cfj:
                cls.spinner = cfj["spinner"]
            if "color" in cfj:
                cls.color = cfj["color"]
            cf.close()
            cls.conf_exists = True
        except FileNotFoundError as ex:
            logger.error("%s was not found", cls.full_file_path)
        except Exception as ex:
            logger.error("An exception occurred while attempting to load %s", cls.full_file_path)
            logger.error(str(ex))

        # Set up current working dir
        cls.cwd = os.path.realpath(os.path.abspath
                                          (os.path.split(inspect.getfile
                                                         (inspect.currentframe()))[0]))

        # If no conf file exists, create one with all defaults
        if not cls.conf_exists:
            QConfiguration.save()
        # The logger defaults to debug level logging.
        # This sets the log level to whatever default was set above.
        the_app_logger.set_log_level(cls.loglevel)

    @classmethod
    def save(cls):
        """
        Save configuraton back to iex.conf
        :return:
        """

        # Make sure folders exist
        if not os.path.exists(cls.file_path):
            os.makedirs(cls.file_path)

        conf = {}
        conf["loglevel"] = cls.loglevel
        conf["font"] = cls.font
        conf["color"] = cls.color
        conf["spinner"] = cls.spinner

        logger.debug("Saving configuration to %s", cls.full_file_path)
        cf = open(cls.full_file_path, "w")
        json.dump(conf, cf, indent=4)
        cf.close()

        cls.conf_exists = True

    @classmethod
    def is_configured(cls):
        """
        The app is configured if the lumiclock.conf file exists
        :return:
        """

        return cls.conf_exists

# Set up configuration
QConfiguration.load()
