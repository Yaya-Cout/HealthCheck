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

# Import dbus daemon
import healthcheck.dbus_daemon

# Set up logging
logger = logging.getLogger(__name__)

# Log the loading of the run module
logger.debug("Loading module: %s from %s", __name__, __file__)


def dbus_main(config):
    """Create and run the DBus service."""
    # Create the DBus service
    service = healthcheck.dbus_daemon.Service(config)

    # Run the DBus service
    service.run()


def run(config):
    """Run the health check."""
    # Log the start of the health check
    logger.info("Starting health check")
    # Run dbus_main
    dbus_main(config)
