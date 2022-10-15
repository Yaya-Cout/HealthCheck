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

# Import the score calculation function
import healthcheck.score

# Import the tests
import healthcheck.tests.command
import healthcheck.tests.cpu
import healthcheck.tests.memory
import healthcheck.tests.load

# Set up logging
logger = logging.getLogger(__name__)

# Log the loading of the run module
logger.debug("Loading module: %s from %s", __name__, __file__)

TESTS = {
    "cpu": healthcheck.tests.cpu.Test,
    "memory": healthcheck.tests.memory.Test,
    "load": healthcheck.tests.load.Test,
}


def run(config):
    """Run the health check."""
    # Initialize the score dictionary
    score = {}

    # Run the tests
    for test_to_perform in config["checks_to_perform"]:
        # Ensure the test config exists
        if test_to_perform not in config["checks"]:
            logger.error("Test config not found: %s", test_to_perform)
            continue

        # Get the test config
        test_config = config["checks"][test_to_perform]

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
                logger.error("Invalid test type: %s", test_config["type"])
                continue
            # Run the test
            test = TESTS[test_config["type"]](test_config)
            result = test.run()
        else:
            logger.error("Invalid test config: %s", test_config)
            continue

        # Check the result
        if result:
            logger.info("Test passed: %s; Output: %s", test_to_perform, result)
            score[test_to_perform] = {
                "score": result,
                "config": test_config,
            }
        else:
            logger.error("Test failed: %s", test_to_perform)
            return False

    # Calculate the score
    score = healthcheck.score.calculate(score, config)

    # Log the score
    logger.info("Score: %s", score)

    # Return the score
    return score
