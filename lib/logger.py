#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307 USA

import logging
import os
from os import path

class Logger:
    """ Wrapper singleton for Python's logging module. """

    def __call__(self):
        return self

    def __init__(self):
        # Set up logger configuration
        level = logging.DEBUG
        format = "%(asctime)s [%(name)s] %(levelname)s %(message)s"
        date = "%a, %d %b %Y %H:%M:%S"

        # Determine log filename
        logfile = path.join(os.getcwd(), "iug", "iug.log")

        # Create i2t data dir if necessary
        if not path.exists(path.dirname(logfile)):
            os.makedirs(path.dirname(logfile))

        # Configure file logging
        logging.basicConfig(level = level, format = format, datefmt = date,
                filename = logfile, filemode = "w")

    def warning(self, domain, message):
        """ Log a warning message. """

        logging.getLogger(domain).warning(message)

    def error(self, domain, message):
        """ Log an error message. """

        logging.getLogger(domain).error(message)

    def debug(self, domain, message):
        """ Log a debug message. """

        logging.getLogger(domain).debug(message)


Logger = Logger()


