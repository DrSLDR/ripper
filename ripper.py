#!/usr/bin/python3

"""
ripper - Batch downloader script
Copyright (C) 2016 Jonas A. Hultén

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from lxml import html
import requests, os, argparse, logging, json

class GenericRipper(object):
    """Generic superclass. Contains all functions subclasses must implement."""

    def __init__(self, name, parent):
        """Constructs the Ripper Generic Object. Contains variables which are
        common among all Ripper objects.

        """
        self.name = name
        self._parent = parent
        self._log = None
        self._config = None

    def _log_declare_entry(self, func):
        """Utility function to debug-log entry into a function."""
        self._log.debug("Entering %s", func.__name__)

    def _log_declare_return(self, func):
        """Utility function to debug-log return from a function (where
        applicable)."""
        self._log.debug("%s returning", func.__name__)

    # pylint: disable=R0201
    def __init_log(self, name):
        """Generic log initialization function.

        Returns the Logger object.

        """
        return logging.getLogger(name)

    def fetch(self, url, tree=True):
        """Generic fetch function. Propagates the call up the parent chain until
        someone handles it.

        Returns a rawdata page or a tree, depending on value of tree.

        """
        self._parent.fetch(url, tree)

    def descend(self, name, ignore_exists=False):
        """Generic descend function. Propagates the call up the parent chain
        until someone handles it.

        Returns True if the call was handled successfully, False otherwise.

        """
        self._parent.descend(name, ignore_exists)

    def ascend(self):
        """Generic ascend function. Propagates the call up the parent chain
        until someone handles it.

        """
        self._parent.ascend()

class Controller(GenericRipper):
    """Controller class. Maintains web session(s), file IO and startup."""

    def __init__(self, arguments=None):
        """Creates the Controller. Takes the argparser argument object as an
        argument.

        """
        super(Controller, self).__init__(name="root", parent=None)
        self._args = arguments
        self._dryrun = True
        self._session = None

    def _is_dryrun(self):
        """Returns true if the current run is dry (no filesystem changes)."""
        return self._dryrun

    def init(self):
        """Initializes the Controller.

        Handles all (legal) commandline arguments passed, initializes logging
        (if used), parses the configuration file, and initializes the requests
        session.

        """
        # Create the log
        self._log = self.__init_log(self._args.loglevel, self._args.logfile,
                                    self.name)

        # Set dry run flag
        self._dryrun = self._args.dryrun
        if self._is_dryrun():
            self._log.info("This is a dry run")
        else:
            self._log.info("This is a live run")

        # Loading the configuration (if neccessary)
        self._config = self.__parse_config(self._args.config)
        if self._config is None:
            self._log.critical("Failed to parse configuration file!")
            exit(1)

        # Create the session
        self._log.debug("Initializing session")
        self._session = self.__init_session()

    def __init_log(self, loglevel, logfile, name):
        """Intializes and sets up the Controller logger configuration.

        Takes the loglevel, logfile, and Controller name as an argument. If
        logfile is None, then logging goes to STDOUT.

        Returns the log object.

        """
        # Figure out loglevel
        if loglevel == 0:
            level = 51
        elif loglevel == 1:
            level = logging.CRITICAL
        elif loglevel == 2:
            level = logging.ERROR
        elif loglevel == 3:
            level = logging.WARNING
        elif loglevel == 4:
            level = logging.INFO
        elif loglevel == 5:
            level = logging.DEBUG

        # Create log
        logging.basicConfig(
            filename=logfile, level=level,
            format="%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s")
        log = logging.getLogger(name)
        log.info("Starting log")
        log.debug("Developer spam sandwich is go!")
        return log

    def __parse_config(self, conffile):
        """Parses the JSON-formatted config file

        Takes the path to the config file as an argument.

        Returns the config structure.

        """
        self._log_declare_entry(self.__parse_config)
        self._log.debug("Opening configuration file at %s", conffile)
        try:
            configf = open(conffile, 'r')
        except OSError as error:
            self._log.critical("Could not open configuration file!")
            self._log.critical(error)
            return None

        self._log.debug("Parsing configuration file")
        try:
            contents = json.load(configf)
        except ValueError as error:
            self._log.critical("Could not parse configuration file!")
            self._log.critical(error)
            configf.close()
            return None

        configf.close()
        self._log.debug("Got configuration %s", contents)
        self._log_declare_return(self.__parse_config)
        return contents

    def __init_session(self):
        """Initializes the web session.

        Returns the session object.

        """
        self._log_declare_entry(self.__init_session)
        session = requests.Session()
        self._log_declare_return(self.__init_session)
        return session

    def fetch(self, url, tree=True):
        """Controller fetch handler. Invokes the session to fetch the website
        given by the URL.

        """
        self._log_declare_entry(self.fetch)
        self._log.info("Fetching %s", url)
        page = self._session.get(url)
        self._log.debug("Got page")
        if tree:
            tree = html.fromstring(page.content)
            self._log_declare_return(self.fetch)
            return tree
        else:
            self._log_declare_return(self.fetch)
            return page

    def descend(self, name, ignore_exists=False):
        """Descends into a directory and creates it if necessary.

        Returns True on successful descension. Returns False if ignore_exists is
        False and the named directory already exists. If a dryrun is running,
        this function does nothing and always returns True.

        """
        self._log_declare_entry(self.descend)

        # Check if this is a dryrun
        if self._is_dryrun():
            self._log.debug("Dry run. Taking no action.")
            self._log_declare_return(self.descend)
            return True

        # Handle descension
        if not os.path.isdir(name):
            self._log.debug("Creating %s", name)
            os.mkdir(name)
        elif not ignore_exists:
            self._log.warning("Directory %s exists. Skipping", name)
            self._log_declare_return(self.descend)
            return False

        self._log.debug("Descending into %s", name)
        os.chdir(name)
        self._log_declare_return(self.descend)
        return True

    def ascend(self):
        """Ascends from a directory.

        Returns nothing, but takes no action if the run is a dryrun."""
        self._log_declare_entry(self.ascend)

        # Check if this is a dryrun
        if self._is_dryrun():
            self._log.debug("Dry run. Taking no action.")
        else:
            self._log.debug("Ascending from directory")
            os.chdir('..')

##### Script block
if __name__ == "__main__":
    # Create the argparser
    PARSER = argparse.ArgumentParser()
    # Prepare the arguments
    PARSER.add_argument("config", help="""Path to the JSON-formatted
                        configuration file.""")
    PARSER.add_argument("-d", "--dry-run", action="store_true", dest="dryrun",
                        help="""Runs without making any changes to the file
                        system.""")
    LOGG = PARSER.add_argument_group("Logging")
    LOGG.add_argument("-l", "--log-file", dest="logfile", default=None,
                      help="""Name of the logfile. Logs to STDOUT if no file
                      name is given.""")
    LOGG.add_argument("-v", "--log-level", dest="loglevel", choices=range(6),
                      default=0, type=int, help="""Log level. 1 is critical
                      level (crashes) only, 5 is debug level. 0 (default)
                      disables logging.""")
    ARGS = PARSER.parse_args()

    # Creates the control
    CONTROLLER = Controller(arguments=ARGS)

    # Initializes the controller
    CONTROLLER.init()
