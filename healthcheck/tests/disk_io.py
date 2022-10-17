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
import psutil

# Set up logging
logger = logging.getLogger(__name__)


class Test:
    """Test class that checks the disk read/write data."""

    def __init__(self, config):
        """Initialize the test."""
        self.config = config
        self.last_run_list = []

        logger.debug("Initializing test: %s", __name__)

    def run(self):
        """Run the test."""
        logger.debug("Running test: %s", __name__)

        # Get the disk I/O data
        disk_io = psutil.disk_io_counters(perdisk=False)

        # Add the read and write data to get the total
        total = disk_io.read_bytes + disk_io.write_bytes

        # Add the total to the last run list
        self.last_run_list.append(total)

        # Remove the oldest entry if the list is too long
        compare_interval = self.config["compare_interval"]
        check_interval = self.config["check_interval"]
        while len(self.last_run_list) > compare_interval / check_interval:
            self.last_run_list.pop(0)

        # Return the average
        return sum(self.last_run_list) / len(self.last_run_list)
