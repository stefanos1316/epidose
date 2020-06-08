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
import socket
from time import sleep
from xmlrpc import client

# The daemon object associated with this program
daemon = None

# Processes to verify
PROCESSES = ["beacon_tx", "beacon_rx"]

FLASH_PAUSE = 3


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
    return proxy.supervisor.getState()["statename"] == "RUNNING"


def process_check(proxy):
    """ Return true if all epidose processes are running."""
    for i in PROCESSES:
        if proxy.supervisor.getProcessInfo(f"epidose:{i}")["statename"] != "RUNNING":
            return False
    return True


def watchdog_check(proxy):
    """ Flash green led if all processes are running """
    if supervisor_check(proxy) and process_check(proxy):
        print("OK")


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
    while True:
        watchdog_check(proxy)
        sleep(FLASH_PAUSE)


if __name__ == "__main__":
    main()
