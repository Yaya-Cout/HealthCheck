#!/usr/bin/env python3
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

# Import dbus
import dbus

BUS_NAME = "org.healthcheck"
OBJECT_PATH = "/org/healthcheck"


class Client():
    """The DBus client for the Health Check."""

    def __init__(self):
        """Initialize the DBus client."""
        bus = dbus.SessionBus()
        service = bus.get_object(
            BUS_NAME,
            OBJECT_PATH
        )
        self.run_all = service.get_dbus_method(
            "run_all",
            f"{BUS_NAME}.Run"
        )
        self.run_check = service.get_dbus_method(
            "run_check",
            f"{BUS_NAME}.Run"
        )
        self.run_needed = service.get_dbus_method(
            "run_needed",
            f"{BUS_NAME}.Run"
        )
        self.get_score = service.get_dbus_method(
            "get_score",
            f"{BUS_NAME}.Score"
        )
        self.get_config = service.get_dbus_method(
            "get_config",
            f"{BUS_NAME}.Config"
        )
        self.set_config = service.get_dbus_method(
            "set_config",
            f"{BUS_NAME}.Config"
        )
        self.quit = service.get_dbus_method("quit", f"{BUS_NAME}.Quit")

    def run(self):
        """Run the DBus client."""
        # Get the score
        score = self.get_score()
        # Print the score
        print(f"Score: {score}")
        # Call all API methods to test them
        self.run_all()
        self.run_check("disk")
        self.run_needed()
        print("Config:")
        print(self.get_config("disk"))
        print(self.get_config("."))
        print(self.get_config("/checks/disk_usage"))
        self.set_config("/checks/disk_usage/disk_test_path", "/tmp")
        print(self.get_config("/checks/disk_usage/disk_test_path"))
        self.set_config("/checks/disk_usage/disk_test_path", "/")
        print(self.get_config("/checks/disk_usage/disk_test_path"))
        # Quit the DBus service
        self.quit()


if __name__ == "__main__":
    Client().run()
