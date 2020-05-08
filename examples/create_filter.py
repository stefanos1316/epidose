#!/usr/bin/env python3

""" Create Cuckoo filter with reported infections """

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
from dp3t.protocols.unlinkable_db import TracingDataBatch
import logging
import sys


def read_seeds(file_path):
    """Return an array containing a pair containing a list of epochs and a
    list of corresponding seeds read from the specified file path."""

    epochs = []
    seeds = []
    with open(file_path, "r") as f:
        for line in f:
            epoch, seed = line.split()
            epochs.append(int(epoch))
            seeds.append(bytearray.fromhex(seed))
    return [(epochs, seeds)]


def main():
    parser = argparse.ArgumentParser(
        description="Create Cuckoo filter with reported infections"
    )
    parser.add_argument(
        "-d", "--debug", help="Run in debug mode logging to stderr", action="store_true"
    )
    parser.add_argument(
        "-D",
        "--database",
        help="Specify the database location",
        default="/var/lib/dp3t/server-database.db",
    )
    parser.add_argument("-s", "--seeds-file", help="File containing epochs and seeds")
    parser.add_argument(
        "-o",
        "--output-file",
        help="File where output will be stored",
        default="cuckoo-filter.bin",
    )
    parser.add_argument(
        "-v", "--verbose", help="Set verbose logging", action="store_true"
    )
    args = parser.parse_args()

    # Setup logging
    global logger
    logger = logging.getLogger("create_filter")
    if args.debug:
        log_handler = logging.StreamHandler(sys.stderr)
    else:
        log_handler = logging.FileHandler("/var/log/create_filter")
    formatter = logging.Formatter("%(asctime)s: %(message)s")
    log_handler.setFormatter(formatter)

    logger.addHandler(log_handler)

    if args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logger.setLevel(log_level)
    log_handler.setLevel(log_level)

    logger.info("Starting up")

    # Obtain seeds
    if args.seeds_file:
        tracing_seeds = read_seeds(args.seeds_file)
    else:
        # TODO Obtain tracing seeds from the server database
        tracing_seeds = ([], [])

    # Create and save filter
    cuckoo_filter = TracingDataBatch(tracing_seeds)
    with open(args.output_file, "wb") as f:
        cuckoo_filter.tofile(f)
    print(cuckoo_filter.capacity)


if __name__ == "__main__":
    main()
