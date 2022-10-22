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
import healthcheck.tests.disk_usage
import healthcheck.tests.disk_io

# Set up logging
logger = logging.getLogger(__name__)

# Log the loading of the run module
logger.debug("Loading module: %s from %s", __name__, __file__)

TESTS = {
    "cpu": healthcheck.tests.cpu.Test,
    "ram": healthcheck.tests.ram.Test,
    "load": healthcheck.tests.load.Test,
    "disk_usage": healthcheck.tests.disk_usage.Test,
    "disk_io": healthcheck.tests.disk_io.Test,
}


class TestManager:
    """Health Check test manager."""

    def __init__(self, config):
        """Initialize the class."""
        # Save the config
        self.config = config

        # Create the test data
        self.test_data = {}

        # Create the test instances cache (so tests can use self to store
        # things)
        self.test_instances = {}

        # Create the score
        self.score = None

        # Create the ready flag (for run_needed)
        self.ready = False

    def run_check_real(self, test_to_perform):
        """Run a single check."""
        # Check if the test config exists
        if test_to_perform not in self.config["checks"]:
            logger.warning("Test config not found: %s", test_to_perform)
            return False
        # Get the config
        test_config = self.config["checks"][test_to_perform]

        # Initialize the test instance if not cached
        if test_to_perform in self.test_instances:
            # Get the test instance
            test = self.test_instances[test_to_perform]

        elif "command" in test_config:
            # Initialize the test
            test = healthcheck.tests.command.Test(
                test_to_perform,
                test_config["command"],
                test_config["command_run_language"],
                test_config.get("regex", None),
            )

            # Add the test to the test instances cache
            self.test_instances[test_to_perform] = test
        elif "type" in test_config:
            # Get if the test type is valid
            if test_config["type"] not in TESTS:
                logger.warning(
                    "Invalid test type: %s",
                    test_config["type"]
                )
                return False

            # Initialize the test
            test = TESTS[test_config["type"]](test_config)

            # Add the test to the test instances cache
            self.test_instances[test_to_perform] = test
        else:
            logger.warning("Invalid test config: %s", test_config)
            return False

        # Run the test and return the result
        if result := test.run():
            logger.info("Test passed: %s; Output: %s", test_to_perform, result)
            return result
        # If the test failed, log it (we don't use an else here, because the
        # previous if statement returns)
        logger.warning("Test failed: %s", test_to_perform)
        return False

    def run_check(self, test_to_perform):
        """Wrap the check run to catch exceptions and update test data."""
        # Ensure that the test config exists
        if test_to_perform not in self.config["checks"]:
            logger.warning("Test config not found: %s", test_to_perform)
            return False

        # Run the test
        try:
            result = self.run_check_real(test_to_perform)
        except Exception:
            logger.error("Error running test: %s", test_to_perform)
            # We return False here, because we don't want to update the test :
            # False is equivalent to zero, and the score calculation function
            # will handle it.
            return False

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
            # Run the test
            if not self.run_check(test_to_perform):
                # If the test failed, don't set the score, and remove the test
                # from the test data (if it exists)
                if test_to_perform in self.test_data:
                    del self.test_data[test_to_perform]
                continue

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

            # Check if the test is in the test data (if not, run it)
            # TODO: Don't rerun tests that failed (or add a timeout before
            # rerunning them)
            if test_to_perform not in self.test_data:
                # Run the test
                if not self.run_check(test_to_perform):
                    # If the test failed, don't set the score, and remove the
                    # test from the test data (if it exists)
                    if test_to_perform in self.test_data:
                        del self.test_data[test_to_perform]
                    continue

                # Add the result to the score list (we copy the test data,
                # because the test data has the score list field, and more)
                score_list[test_to_perform] = self.test_data[test_to_perform]
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

        # Restore the logging level
        logging.disable(logging.NOTSET)

        # Return the score
        return self.score

    def reload_score(self):
        """Reload the score."""
        self.score = healthcheck.score.calculate(self.test_data, self.config)
