"""Health Check - A simple health check script for your server."""

# This file is part of the healthcheck package.
#
# The healthcheck package is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# The healthcheck package is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# the healthcheck package.  If not, see <http://www.gnu.org/licenses/>.

# Standard library imports
import logging
import asyncio

# Import dbus and gobject
import dbus
import dbus.service
import dbus.mainloop.glib
try:
    from GLib import MainLoop as gobject
except ImportError:
    try:
        from gi.repository import GObject as gobject
    except ImportError:
        import gobject

# Import healthcheck modules
import healthcheck.test_manager

# Set up logging
logger = logging.getLogger(__name__)

# Log the loading of the dbus_daemon module
logger.debug("Loading module: %s from %s", __name__, __file__)

# Initialize constants
BUS_NAME = "org.healthcheck"
OBJECT_PATH = "/org/healthcheck"


class Service(dbus.service.Object):
    """The DBus service for the Health Check."""

    def __init__(self, config):
        """Initialize the DBus service."""
        # Log the initialization of the DBus service
        logger.debug("Initializing DBus service")

        # Initialize the DBus main loop
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        # Initialize the DBus service
        bus_name = dbus.service.BusName(BUS_NAME, dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, OBJECT_PATH)

        # Initialize the test manager
        self._test_manager = healthcheck.test_manager.TestManager(config)

        # Initialize the gobject loop
        self._loop = gobject.MainLoop()

        # Add the run_needed method to the gobject loop
        gobject.idle_add(self._test_manager.run_needed)

        # Save the config
        self._config = config

        # Initialize the score
        self._score = None

    def run(self):
        """Run the DBus service."""
        # Log the starting of the DBus service
        logger.debug("Starting DBus service")

        # Run the checks
        self._score = self._test_manager.run_all()

        # Log the start of the DBus service
        logger.info("DBus service started")
        self._loop.run()
        logger.info("DBus service stopped")

    @dbus.service.method(
        f"{BUS_NAME}.Run",
        in_signature='',
        out_signature='',
    )
    def run_all(self):
        """Run all the tests."""
        # Log the running of all the tests
        logger.debug("Running all tests")

        # Run the tests
        self._test_manager.run_all()

    @dbus.service.method(
        f"{BUS_NAME}.Run",
        in_signature='s',
        out_signature=''
    )
    def run_check(self, check_name):
        """Run a check."""
        # Log the running of a test
        logger.debug("Running test: %s", check_name)

        # Run the test
        self._test_manager.run_check(check_name)

        # Reload the score
        self._test_manager.reload_score()

    @dbus.service.method(
        f"{BUS_NAME}.Run",
        in_signature='',
        out_signature=''
    )
    def run_needed(self):
        """Run the tests that are needed."""
        self._test_manager.run_needed()


    @dbus.service.method(
        f"{BUS_NAME}.Score",
        in_signature='',
        out_signature='d',
    )
    def get_score(self):
        """Get the score."""
        # Log the getting of the score
        logger.debug("Getting score")

        # Return the score
        return self._test_manager.score

    @dbus.service.method(
        f"{BUS_NAME}.Quit",
        in_signature='',
        out_signature=''
    )
    def quit(self):
        """Quit the DBus service."""
        self._loop.quit()
