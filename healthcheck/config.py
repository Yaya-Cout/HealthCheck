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
import os
import logging

import yaml

# Set up logging
logger = logging.getLogger(__name__)

# Log the loading of the config module
logger.debug("Loading module: %s from %s", __name__, __file__)


DEFAULT_CONFIG = {
    # Default configuration, to avoid very long checks definitions
    "default_checks_config": {
        "coeff": 1,
        "check_interval": 10,
        "check_timeout": 10,
        "min": 0,
        "max": 100,
        "lower_is_better": True,
        "very_low": 10,
        "low": 20,
        "quite_low": 30,
        "normal": 40,
        "quite_high": 50,
        "high": 60,
        "very_high": 70,
        "warning": 80,
        "critical": 90,
        "very_critical": 95,
        "extremely_critical": 99,
        "extreme": 100,
        # For the "command" check
        "command_run_language": "C",
        "ignore_if_up_average": False,
    },
    # Here we define the checks settings (command and regex, or type for
    # special checks)
    "checks": {
        "load": {
            "type": "load",
            "coeff": 1,
            "min": 0,
            "max": 50,
            "ignore_if_up_average": True,
        },
        "cpu": {
            "type": "cpu",
            "coeff": 2,
            "cpu_test_duration": 1,
        },
        "ram": {
            "type": "ram",
            "coeff": 2,
        },
        "disk_usage": {
            "type": "disk_usage",
            "coeff": 2,
            "ignore_if_up_average": True,
            "disk_test_path": "/",
        },
        "disk_io": {
            "type": "disk_io",
            "coeff": 2,
            "ignore_if_up_average": True,
            "compare_interval": 60,
        },
    },
    # Here we define the checks to be performed
    "checks_to_perform": [
        "load",
        "cpu",
        "ram",
        "disk_usage",
        "disk_io",
        "users",
        "processes",
    ],
    # Here we define the global configuration (score calculation, etc.)
    "global": {
        "score": {
            "lower_is_better": False,
            "min": 0,
            "max": 100,
        },
    }
}


def replace_default_config(config, default_config):
    """Add default values to the configuration (Recursive)."""
    # Iterate over the configuration
    for key, value in default_config.items():
        # If the key is not in the configuration, add it
        if key not in config:
            config[key] = value

        # Check if the type of the value is the same as the default value, and
        # if not, replace it and print a warning
        elif not isinstance(config[key], type(value)):
            logger.warning(
                "The value of the key '%s' is not valid, replacing it with the"
                " default value.", key
            )
            config[key] = value

        # If the value is a dict, call the function recursively
        elif isinstance(value, dict):
            config[key] = replace_default_config(config[key], value)

    return config


def load(config_file):
    """Load the configuration from the YAML file."""
    # Check if the configuration file exists
    if not os.path.isfile(config_file):
        print("Configuration file not found, creating a default one.")
        init(config_file)

    # Load the configuration file
    with open(config_file, "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.SafeLoader)

    # Set the default configuration for missing values
    config = replace_default_config(config, DEFAULT_CONFIG)

    # Copy the default checks configuration (from the user configuration) to
    # the checks configuration
    for check in config["checks"]:
        # Copy the default checks configuration to the check configuration for
        # missing values
        config["checks"][check] = replace_default_config(
            config["checks"][check], config["default_checks_config"]
        )
    return config


def init(config_file):
    """Create a default configuration file."""
    with open(config_file, "w") as config_file:
        # Dump the default configuration with YAML formatting
        yaml.dump(DEFAULT_CONFIG, config_file, default_flow_style=False)


def parse_path(config, path):
    """Parse a path in the configuration file."""
    # Replace slashes with dots
    path = path.replace("/", ".")
    # Remove the dots at the beginning and end
    path = path.strip(".")
    # If the path is empty or is just a dot, return the whole config
    if path in ["", "."]:
        return "", config

    # Else, split the path into a list and parse the config
    path = path.split(".")

    # Get the config
    for key in path:
        # Ensure the key exists
        if key not in config:
            logger.warning("Path %s does not exist in config", path)
            return "", {}

        # Get the next part of the config
        # In case of a dict that return a value, we should return the
        # key, not the value
        if isinstance(config[key], (dict, list)):
            config = config[key]
        else:
            config = config.get(key)
    return path, config


def set_path(config, path, value):
    """Set a value in the configuration file."""
    # Parse the path
    path = parse_path(config, path)[0]

    # Return the new config
    return _set_config(config, path, value)


def _set_config(config, path: list[str | list], value):
    """Set a value in the configuration file."""
    # If the path is only one element, set the value
    if len(path) == 1:
        config[path[0]] = value
        return config

    # Else, get the next part of the path
    key = path.pop(0)

    # Assert the key exists (should be done when parsing the path)
    assert key in config

    # Set the value in the next part of the config
    config[key] = _set_config(config[key], path, value)
    return config
