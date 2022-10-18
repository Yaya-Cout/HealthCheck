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
import subprocess
import re

# Set up logging
logger = logging.getLogger(__name__)


class Test:
    """Special test class that run commands."""

    def __init__(self, name, command, command_run_language, regex=None):
        """Initialize the test."""
        self.name = name
        self.command = command
        self.command_run_language = command_run_language
        self.regex = regex
        logger.debug(
            "Initializing test: %s with command: %s",
            self.name,
            self.command
        )

    def run(self):
        """Run the test."""
        logger.debug("Running test: %s", self.name)
        logger.debug("Command: %s", self.command)

        # Run the command
        try:
            output = subprocess.check_output(
                self.command,
                shell=True,
                universal_newlines=True,
                env={"LANG": self.command_run_language}
            )
        except subprocess.CalledProcessError as error:
            logger.warning("Command failed with error code: %s",
                         error.returncode)
            logger.warning("Command output: %s", error.output)
            return False

        # Convert the output to a string
        # output = output.decode("utf-8")

        if self.regex:
            # Iterate over regex
            for regex in self.regex:
                if match := re.search(regex, output):
                    output = match[0]
                    logger.debug("Regex found: %s; output: %s", regex, output)

                else:
                    logger.error("Regex not found: %s", regex)
                    return False
        # Parse the output to a float
        try:
            output = float(output)
        except ValueError:
            logger.error("Could not parse output: %s", output)
            return False

        # Return the output
        return output
