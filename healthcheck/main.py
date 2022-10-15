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
import argparse
import logging

# Third party imports
rich_logger = False
try:
    from rich.logging import RichHandler
    rich_logger = True
except ModuleNotFoundError:
    # Fall back to the standard logging handler (a bit ugly, to avoid an if on
    # initialization)
    from logging import StreamHandler as RichHandler

# Local imports
# import healthcheck
from healthcheck.__version__ import __version__
import healthcheck.config
import healthcheck.run

# Set up logging
logger = logging.getLogger(__name__)


def main():
    """Entry point for the healthcheck package."""
    # Create the argument parser
    parser = argparse.ArgumentParser(
        description="Health Check - A simple health check script for your server."
    )
    parser.add_argument(
        "-c",
        "--config",
        default="healthcheck.yml",
        help="The path to the health check configuration file.",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Enable debug logging.",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )


    # Parse the arguments
    args = parser.parse_args()

    # Set up logging
    if rich_logger:
        logging.basicConfig(
            level=logging.DEBUG if args.debug else logging.INFO,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler()]
        )
    else:
        logging.basicConfig(
            format="%(asctime)s: %(levelname)s: %(name)s: %(message)s",
            level=logging.DEBUG if args.debug else logging.INFO,
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # Load the configuration
    config = healthcheck.config.load(args.config)

    # Run the health checks
    healthcheck.run.run(config)
