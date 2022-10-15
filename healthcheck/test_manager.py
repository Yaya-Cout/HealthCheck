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
# import asyncio
import time

# Import the score calculation function
import healthcheck.score

# Import the tests
import healthcheck.tests.command
import healthcheck.tests.cpu
import healthcheck.tests.ram
import healthcheck.tests.load

# Set up logging
logger = logging.getLogger(__name__)

# Log the loading of the run module
logger.debug("Loading module: %s from %s", __name__, __file__)

TESTS = {
    "cpu": healthcheck.tests.cpu.Test,
    "ram": healthcheck.tests.ram.Test,
    "load": healthcheck.tests.load.Test,
}


class TestManager:
    """Health Check test manager."""

    def __init__(self, config):
        """Initialize the class."""
        # Save the config
        self.config = config

        # Create the test data
        self.test_data = {}

        # Create the score
        self.score = None

        # Create the ready flag (for run_needed)
        self.ready = False

    def run_check_real(self, test_to_perform):
        """Run a single check."""
        # Get the config
        test_config = self.config["checks"][test_to_perform]

        # Get if test has command field
        if "command" in test_config:
            # Run the command test
            test = healthcheck.tests.command.Test(
                test_to_perform,
                test_config["command"],
                test_config["command_run_language"],
                test_config.get("regex", None),
            )
            result = test.run()
        elif "type" in test_config:
            # Get if the test type is valid
            if test_config["type"] not in TESTS:
                logger.warning("Invalid test type: %s", test_config["type"])
                return False
            # Run the test
            test = TESTS[test_config["type"]](test_config)
            result = test.run()
        else:
            logger.warning("Invalid test config: %s", test_config)
            return False

        # Check the result
        if result:
            logger.info("Test passed: %s; Output: %s", test_to_perform, result)
            return result
        else:
            logger.warning("Test failed: %s", test_to_perform)
            return False

    def run_check(self, test_to_perform):
        """Wrap the check run to catch exceptions and update test data."""
        # Run the test
        try:
            result = self.run_check_real(test_to_perform)
        except Exception:
            logger.error("Error running test: %s", test_to_perform)
            result = False

        # Add the result to the test data
        self.test_data[test_to_perform] = {
            "score": result,
            "config": self.config["checks"][test_to_perform],
            "last_run": time.time(),
            "run_at": time.time() +
            self.config["checks"][test_to_perform]["check_interval"],
        }

        # Return the result
        return result

    def run_all(self):
        """Run the health check."""
        # Initialize the score dictionary
        score_list = {}

        # Run the tests
        for test_to_perform in self.config["checks_to_perform"]:
            # Ensure the test config exists
            if test_to_perform not in self.config["checks"]:
                logger.warning("Test config not found: %s", test_to_perform)
                continue

            # Run the test
            self.run_check(test_to_perform)

            # Add the result to the score list (we copy the test data, because
            # the test data has the score list field, and more)
            score_list[test_to_perform] = self.test_data[test_to_perform]

        # Reload the score
        self.reload_score()

        # Mark the manager as ready
        self.ready = True

        # Log the score
        logger.info("Score: %s", self.score)

        # Return the score
        return self.score

    def run_needed(self):
        """Run tests that need to be re-run."""
        # Disable logging for this function (it's called a lot)
        last_level = logger.getEffectiveLevel()
        logging.disable(logging.CRITICAL)

        # Check if the manager is ready
        if not self.ready:
            return False

        # Initialize the score dictionary
        score_list = {}

        # Run the tests
        for test_to_perform in self.config["checks_to_perform"]:
            # Ensure the test config exists
            if test_to_perform not in self.config["checks"]:
                # logger.warning("Test config not found: %s", test_to_perform)
                continue

            # Check if the test needs to be run
            if self.test_data[test_to_perform]["run_at"] < time.time():
                # Run the test
                self.run_check(test_to_perform)

            # Add the result to the score list (we copy the test data, because
            # the test data has the score list field, and more)
            score_list[test_to_perform] = self.test_data[test_to_perform]

        # Reload the score
        self.reload_score()

        # Log the score
        logger.info("Score: %s", self.score)

        # Restore logging
        logging.disable(last_level)

        # Return the score
        return self.score

    def reload_score(self):
        """Reload the score."""
        self.score = healthcheck.score.calculate(self.test_data, self.config)
