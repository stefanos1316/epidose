#!/usr/bin/env python3

""" Read the Cuckoo filter and check infection risk based on contacts. """

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
from dp3t.protocols.unlinkable_db import TracingDataBatch, ContactTracer
import logging
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Read Cuckoo filter and check against contacts"
    )
    parser.add_argument(
        "-d", "--debug", help="Run in debug mode logging to stderr", action="store_true"
    )
    parser.add_argument(
        "-D",
        "--database",
        help="Specify the database location",
        default="/var/lib/epidose/client-database.db",
    )
    parser.add_argument("-o", "--observation", help="Observation hash to check")
    parser.add_argument(
        "-v", "--verbose", help="Set verbose logging", action="store_true"
    )
    parser.add_argument("filter", help="Cuckoo filter file")
    parser.add_argument("capacity", type=int, help="Cuckoo filter file capacity")
    args = parser.parse_args()

    # Setup logging
    global logger
    logger = logging.getLogger("check_infection")
    if args.debug:
        log_handler = logging.StreamHandler(sys.stderr)
    else:
        log_handler = logging.FileHandler("/var/log/check_infection")
    formatter = logging.Formatter("%(asctime)s: %(message)s")
    log_handler.setFormatter(formatter)

    logger.addHandler(log_handler)

    if args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logger.setLevel(log_level)
    log_handler.setLevel(log_level)

    logger.debug("Starting up")
    with open(args.filter, "rb") as f:
        cuckoo_filter = TracingDataBatch(fh=f, capacity=args.capacity)

    if args.observation:
        if (
            bytes(bytearray.fromhex(args.observation))
            in cuckoo_filter.infected_observations
        ):
            print("Found")
            sys.exit(0)
        else:
            print("Not found")
            sys.exit(1)
    else:
        ct = ContactTracer(None, args.database, transmitter=False, receiver=False)
        matches = ct.matches_with_batch(cuckoo_filter)
        print(matches)
        sys.exit(0 if matches == 0 else 1)


if __name__ == "__main__":
    main()
