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
from dp3t.protocols.server_database import ServerDatabase
from dp3t.protocols.unlinkable_db import TracingDataBatch
from epidose.common.daemon import Daemon
import os
from tempfile import mkstemp

# The daemon object associated with this program
daemon = None

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
        default="/var/lib/epidose/server-database.db",
    )
    parser.add_argument("-s", "--seeds-file", help="File containing epochs and seeds")
    parser.add_argument(
        "-v", "--verbose", help="Set verbose logging", action="store_true"
    )
    parser.add_argument("filter", help="File where filter will be stored")
    args = parser.parse_args()

    # Setup logging
    daemon = Daemon("create_filter", None, args)
    global logger
    logger = daemon.get_logger()

    # Obtain seeds
    if args.seeds_file:
        tracing_seeds = read_seeds(args.seeds_file)
    else:
        db = ServerDatabase(args.database)
        tracing_seeds = [db.get_epoch_seeds_tuple()]

    # Create and save filter
    cuckoo_filter = TracingDataBatch(tracing_seeds)
    handle, name = mkstemp(dir=os.path.dirname(args.filter))

    # Write filter to a temparary file
    with os.fdopen(handle, "wb") as f:
        f.write(cuckoo_filter.capacity.to_bytes(8, byteorder="big", signed=False))
        cuckoo_filter.tofile(f)

    # Atomically replace any existing filter file with the new one
    logger.debug(f"Rename {name} to {args.filter}")
    os.rename(name, args.filter)


if __name__ == "__main__":
    main()
