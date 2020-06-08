#!/usr/bin/env python3

"""Common daemon behavior"""

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

from daemonize import Daemonize
import logging
import sys


class Daemon(object):
    def __init__(self, name, main, main_args):
        """Construct a new daemon given its name, main function, and
        parsed arguments."""
        # Setup logging
        self.logger = logging.getLogger(name)

        # Set global arguments
        self.args = main_args

        # Display log messages only on defined handlers.
        self.logger.propagate = False

        if self.args.debug:
            # Logging output goes to stderr
            log_handler = logging.StreamHandler(sys.stderr)
            keep_fds = None
        else:
            # Logging output goes to file
            log_handler = logging.FileHandler(f"/var/log/{name}")
            keep_fds = [log_handler.stream.fileno()]

        # Messages are preceded by timestamp
        formatter = logging.Formatter("%(asctime)s: %(message)s")
        log_handler.setFormatter(formatter)

        self.logger.addHandler(log_handler)

        if self.args.verbose:
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO
        self.logger.setLevel(log_level)
        log_handler.setLevel(log_level)

        # Run as a daemon
        self.daemon = Daemonize(
            app=name,
            pid=f"/run/{name}.pid",
            action=main,
            keep_fds=keep_fds,
            logger=self.logger,
            foreground=self.args.debug,
        )

    def start(self):
        """Start the underlying daemon."""
        self.daemon.start()

    def get_logger(self):
        """Return a logger given the name and the program's arguments."""
        return self.logger

    def get_args(self):
        """Return the parsed arguments passed to the constructor."""
        return self.args
