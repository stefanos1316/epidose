#!/usr/bin/env python3

"""Common logging behavior"""

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

import logging
import sys


class LoggerWriter(object):
    """Write messages, handling embedded newlines."""

    def __init__(self, level):
        self.level = level
        self.msg = ""

    def write(self, message):
        """Create separate messages for embedded newlines"""
        self.msg = self.msg + message
        while "\n" in self.msg:
            pos = self.msg.find("\n")
            self.level(self.msg[:pos])
            self.msg = self.msg[pos + 1 :]

    def flush(self):
        if self.msg != "":
            self.level(self.msg)
            self.msg = ""


def getLogger(name, args):
    """Return a logger given the name and the program's arguments."""

    logger = logging.getLogger(name)
    if args.debug:
        # Logging output goes to stderr
        log_handler = logging.StreamHandler(sys.stderr)
    else:
        # Logging output goes to file
        log_handler = logging.FileHandler(f"/var/log/{name}")
        # Stderr gos to file
        sys.stderr = LoggerWriter(logger.error)
        # Messages are preceded by timestamp
        formatter = logging.Formatter("%(asctime)s: %(message)s")
        log_handler.setFormatter(formatter)

    logger.addHandler(log_handler)

    if args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logger.setLevel(log_level)
    log_handler.setLevel(log_level)

    if not args.debug:
        logger.info("Starting up")
    return logger
