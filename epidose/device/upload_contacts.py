#!/usr/bin/env python3

""" Upload specified contact seeds to the server """

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
from dp3t.protocols.unlinkable_db import ContactTracer
from datetime import datetime
from epidose.common import logging
import requests
from sys import exit


# TODO: Change this, or pass a parameter
SERVER_URL = "https://api.contact-tracing.org"


def main():
    parser = argparse.ArgumentParser(description="Contact tracing beacon trasmitter")
    parser.add_argument(
        "-a", "--authorization", help="Upload authorization code", default=":NONE:"
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
    parser.add_argument("-t", "--test", help="Test script", action="store_true")
    parser.add_argument("-s", "--server", help="Server URL", default=SERVER_URL)
    parser.add_argument(
        "-v", "--verbose", help="Set verbose logging", action="store_true"
    )
    parser.add_argument(
        "start_time", help="The (ISO) time from which contact tracing should start"
    )
    parser.add_argument(
        "end_time", help="The (ISO) time at which contact tracing should end"
    )
    args = parser.parse_args()

    if args.test:
        args.debug = True
        args.database = ":memory:"

    # Setup logging
    global logger
    logger = logging.getLogger("upload_contacts", args)

    # Obtain the specified seeds
    ct = ContactTracer(None, args.database, transmitter=False, receiver=False)
    (epochs, seeds) = ct.get_tracing_information(
        datetime.fromisoformat(args.start_time), datetime.fromisoformat(args.end_time)
    )

    # Create dictionary for JSON
    logger.debug("Creating request")
    post = {"authorization": args.authorization, "data": []}
    i = 0
    for e in epochs:
        post["data"].append({"epoch": e, "seed": seeds[i].hex()})
        i += 1

    # Send request and check response
    logger.debug("Sending request")
    res = requests.post(f"{args.server}/add_contagious", json=post)
    logger.debug("Request sent")
    exit(0 if res.ok else 1)


if __name__ == "__main__":
    main()
