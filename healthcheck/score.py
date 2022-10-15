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

# Set up logging
logger = logging.getLogger(__name__)


def _global_score(score, config):
    """Calculate the global score."""
    # Get the minimum and maximum global score
    global_min_score = config["global"]["score"]["min"]
    global_max_score = config["global"]["score"]["max"]

    # Get the global score percentage
    score_percentage = (score - global_min_score) /\
                       (global_max_score - global_min_score)\
        * global_max_score

    # Ensure the score percentage is between min and max
    score_percentage = max(
        global_min_score,
        min(
            global_max_score,
            score_percentage
        )
    )

    # Convert the score if needed (lower is better)
    if not config["global"]["score"]["lower_is_better"]:
        score_percentage = global_max_score - score_percentage

    # Return the score
    return score_percentage


def calculate(score_list, config):
    """Calculate the score from a list of scores."""
    # Move ignore if up average at the end of the list (we need to know the
    # average of the other tests). It's stored in
    # score_list[item]["config"]["ignore_if_up_average"]
    ignore_if_up_average = score_list.copy()
    for item, value in score_list.items():
        if value["config"]["ignore_if_up_average"]:
            del ignore_if_up_average[item]
            ignore_if_up_average[item] = value

    # Replace the score_list with the new one
    score_list = ignore_if_up_average

    # Create a copy of the score list without the config part of each subdict
    # (for logging purpose)
    score_list_copy = {item: value["score"] for item, value in score_list.items()}
    logger.debug("Calculating score from list: %s", score_list_copy)

    # Initialize the score
    score = 0

    # Total number of coefficients, used to calculate the average
    total_coefficients = 0

    # Loop over the scores
    for item, value in score_list.items():
        # Get the score
        score_item = value["score"]
        # Get the minimum and maximum score
        score_min = value["config"]["min"]
        score_max = value["config"]["max"]

        # Get the score percentage
        score_percentage = (score_item - score_min) / (score_max - score_min) * 100

        # Ensure the score percentage is between 0 and 100
        score_percentage = max(0, min(100, score_percentage))

        # Get the coefficient
        coefficient = value["config"]["coeff"]

        # Compute the score to add
        score_to_add = score_percentage * coefficient
        # If the test is ignored if the average is up, we need to check the
        # average
        if value["config"]["ignore_if_up_average"]:
            # Get the actual average
            actual_average = score / total_coefficients
            # Get the average with the current test
            average_with_current_test = (score + score_to_add) /\
                                        (total_coefficients + coefficient)
            # If the average with the current test is up, we ignore the test.
            # We need to invert the score to check if the average is up,
            # because the score is reversed after the calculation.
            if average_with_current_test < actual_average:
                # For the logging, we need to invert the score if needed
                if not config["global"]["score"]["lower_is_better"]:
                    average_with_current_test = 100 - average_with_current_test
                    actual_average = 100 - actual_average
                logger.debug("Test %s ignored because it would increase the "
                             "average (current average: %s, average with "
                             "test: %s)", item, actual_average,
                             average_with_current_test)
                continue
        score += score_percentage * coefficient

        # Add the coefficient to the total number of coefficients
        total_coefficients += coefficient

        # Calculate the average temporary score
        temp_score = score / total_coefficients

        # Calculate the temporary global score
        temp_global_score = _global_score(temp_score, config)

        # Log the temporary score
        logger.debug(
            "Score with %s: %s", item, temp_global_score
        )

    # Calculate the average score
    score = score / total_coefficients

    # Calculate the global score
    score_percentage = _global_score(score, config)

    # Log the score
    logger.debug("Score: %s", score_percentage)

    # Return the score
    return score_percentage
