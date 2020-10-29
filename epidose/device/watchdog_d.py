#!/usr/bin/env python3

""" Contact tracing device watchdog """

__copyright__ = """
    Copyright 2020 Diomidis Spinellis

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
__license__ = "Apache 2.0"

import argparse
from http.client import HTTPConnection
from epidose.common.daemon import Daemon
from epidose.device.device_io import (
    get_battery_voltage,
    green_led_set,
    led_change_age,
    red_led_set,
    schedule_power_off,
    setup_leds,
)
from os import system
import socket
from sys import exit
from time import sleep
from xmlrpc import client

# Voltage level at which the device shuts down (V)
SHUTDOWN_VOLTAGE = 3.45

# The daemon object associated with this program
daemon = None

# Processes to verify
PROCESSES = ["beacon_rx", "beacon_tx", "update_filter", "upload_seeds", "wps_scanner"]

# Check state (and flash LED if needed) every so many seconds
CHECK_INTERVAL = 2

# LED heartbeat timing
FLASH_PAUSE = 0.1
FLASH_BLINK = 0.05


# Routines to allow connection over a Unix domain socket
# See https://stackoverflow.com/a/51377201/20520
class UnixStreamHTTPConnection(HTTPConnection):
    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.host)


class UnixStreamTransport(client.Transport, object):
    def __init__(self, socket_path):
        self.socket_path = socket_path
        super(UnixStreamTransport, self).__init__()

    def make_connection(self, host):
        return UnixStreamHTTPConnection(self.socket_path)


def supervisor_check(proxy):
    """Return true if supervisor is running"""
    # Might fail due to an exception.  In this case the watchdog will
    # cease operating and the fault will become visible.
    if proxy.supervisor.getState()["statename"] == "RUNNING":
        return True
    else:
        logger.error("supervisord not running")
        return False


def process_check(proxy):
    """ Return true if all epidose processes are running."""
    for i in PROCESSES:
        if proxy.supervisor.getProcessInfo(f"epidose:{i}")["statename"] != "RUNNING":
            logger.error(f"{i} not running")
            return False
    return True


def watchdog_check(proxy):
    """ Flash green led if all processes are running """
    return supervisor_check(proxy) and process_check(proxy)


def main():
    parser = argparse.ArgumentParser(description="Contact tracing beacon receiver")
    parser.add_argument(
        "-d", "--debug", help="Run in debug mode logging to stderr", action="store_true"
    )
    parser.add_argument(
        "-D",
        "--database",
        help="Specify the database location",
        default="/var/lib/epidose/client-database.db",
    )
    parser.add_argument(
        "-v", "--verbose", help="Set verbose logging", action="store_true"
    )
    args = parser.parse_args()

    daemon = Daemon("watchdog", args)

    # Setup logging
    global logger
    logger = daemon.get_logger()

    # Setup server connection
    proxy = client.ServerProxy(
        "http://localhost", transport=UnixStreamTransport("/run/supervisor.sock")
    )
    setup_leds()
    red_led_set(False)
    while True:
        if watchdog_check(proxy):
            # Signal heartbeat if no other signalling is active
            if led_change_age() > CHECK_INTERVAL * 2:
                green_led_set(True)
                sleep(FLASH_BLINK)
                green_led_set(False)
                sleep(FLASH_PAUSE)
                green_led_set(True)
                sleep(FLASH_BLINK)
                green_led_set(False)
        v = get_battery_voltage()
        logger.debug(f"Battery {v}")
        # Graceful shutdown when needed
        if v < SHUTDOWN_VOLTAGE:
            logger.debug("Battery exchausted; shutting down")
            schedule_power_off()
            system("shutdown now 'Battery exhausted (${v} V)'")
            exit(0)
        sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
