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
import yaml

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
