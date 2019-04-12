# -*- coding: UTF-8 -*-
#
# LumiClock application configuration
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
    fontsize = 0
    spinner = "spiral_triangles.gif"
    color = "#EC3818"
    loglevel = "debug"
    backlight = 128
    pirsensor = False
    timeout = 10 * 60
    timein = 10
    debugdisplay = True
    # GPIO 18 or BCM pin 12
    pirpin = 12
    cwd = ""
    conf_exists = False

    @classmethod
    def load(cls):
        """
        Load application settings from configuration file. The location of the lumiclock.conf
        file is OS dependent.
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
            if "fontsize" in cfj:
                try:
                    cls.fontsize = int(cfj["fontsize"])
                except:
                    logger.error("Invalid fontsize value: %s", cfj["fontsize"])
            if "spinner" in cfj:
                cls.spinner = cfj["spinner"]
            if "color" in cfj:
                cls.color = cfj["color"]
            if "pirsensor" in cfj:
                if cfj["pirsensor"].lower() in ["true", "on", "1"]:
                    cls.pirsensor = True
                else:
                    cls.pirsensor = False
            if "timeout" in cfj:
                try:
                    cls.timeout = int(cfj["timeout"])
                except:
                    logger.error("Invalid configuration value for timeout: %s", cfj["timeout"])
            if "timein" in cfj:
                try:
                    cls.timein = int(cfj["timein"])
                except:
                    logger.error("Invalid configuration value for timein: %s", cfj["timein"])
            if "debugdisplay" in cfj:
                cls.debugdisplay = cfj["debugdisplay"].lower() in ["true", "on", "1"]
            if "backlight" in cfj:
                try:
                    cls.backlight = int(cfj["backlight"])
                    # Enforce 0 <= backlight <= 255
                    cls.backlight = min(cls.backlight, 255)
                    cls.backlight = max(cls.backlight, 0)
                except:
                    logger.error("Invalid configuration value for backlight: %s", cfj["backlight"])
            if "pirpin" in cfj:
                try:
                    pin = int(cfj["pirpin"])
                    # Enforce 3 <= pirpin <= 40
                    if pin < 3 or pin > 40:
                        raise ValueError("Invalid configuration value for pirpin: %s", str(cfj["pirpin"]))
                    cls.pirpin = pin
                except ValueError as ex:
                    logger.error(ex)
                except:
                    logger.error("Invalid configuration value for backlight: %s", cfj["backlight"])
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

        # Dump the config for debugging purposes
        QConfiguration.log_dump()

    @classmethod
    def save(cls):
        """
        Save configuraton back to iex.conf
        :return:
        """

        # Make sure folders exist
        if not os.path.exists(cls.file_path):
            os.makedirs(cls.file_path)

        conf = QConfiguration.to_dict()

        logger.debug("Saving configuration to %s", cls.full_file_path)
        cf = open(cls.full_file_path, "w")
        json.dump(conf, cf, indent=4)
        cf.close()

        cls.conf_exists = True

    @classmethod
    def log_dump(cls):
        conf = QConfiguration.to_dict()

        logger.debug("Dumping configuration file %s", cls.full_file_path)
        logger.debug(json.dumps(conf, indent=4))

    @classmethod
    def to_dict(cls):
        """
        Make a dict from the configuration properties
        :return:
        """
        conf = {}
        conf["loglevel"] = cls.loglevel
        conf["font"] = cls.font
        conf["color"] = cls.color
        conf["spinner"] = cls.spinner
        conf["pirsensor"] = str(cls.pirsensor)
        conf["timeout"] = cls.timeout
        conf["timein"] = cls.timein
        conf["debugdisplay"] = str(cls.debugdisplay)
        conf["fontsize"] = cls.fontsize
        conf["backlight"] = cls.backlight
        conf["pirpin"] = cls.pirpin
        return conf

    @classmethod
    def is_configured(cls):
        """
        The app is configured if the lumiclock.conf file exists
        :return:
        """

        return cls.conf_exists

# Set up configuration
QConfiguration.load()
