#!/usr/bin/env python3

""" Contact tracing beacon transmitter """

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
from dp3t.config import EPOCH_LENGTH
from datetime import datetime
from dp3t.protocols.unlinkable_db import ContactTracer
import logging
import subprocess
import sys
import time


def set_transmit(interface, ephid, rssi):
    """Set the Bluetooth low energy beacon to transmit on the specified
    interface the given 16-byte ephid with the given received signal
    strength indication (rssi).
    The beacon uses the AltBeacon format.
    For now the beacon code starts with ED 05 01 01, followed by the ephid.
    See https://github.com/AltBeacon/spec
    """

    assert len(ephid) == 16
    assert rssi >= 0 and rssi < 255

    cmd = [
        "hcitool",
        "-i",
        f"{interface}",
        "cmd",
        "0x08",
        "0x0008",
        "1E",
        "02",
        "01",
        "1A",
        "1b",  # Advertisement length
        "ff",  # Manufacturer-specific data structure
        "f1",
        "05",  # Manufacturer id: 0x05f1 Linux Foundation
        "be",  # ... continue
        "ac",  # AltBeacon code
        "ed",  # ... continue
        "05",  # Contact tracing id
        "01",  # Contact tracing protocol version
        "01",  # Contact tracing application (ephId beacon)
    ]

    # Add ephid
    ephid = ephid.hex()
    for p in range(0, 32, 2):
        cmd.append(ephid[p : p + 2])

    cmd.append(format(rssi, "x"))  # Reference RSSI
    cmd.append("01")  # Manufacturer reserved
    logger.debug(" ".join(cmd))
    if dry_run:
        return
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"{cmd[0]} failed with code {e.returncode}: {e.stderr}")
    except OSError as e:
        logger.error(f"Failed to run {cmd[0]}: {e.strerror}")


def main():
    parser = argparse.ArgumentParser(description="Contact tracing beacon trasmitter")
    parser.add_argument(
        "-d", "--debug", help="Run in debug mode logging to stderr", action="store_true"
    )
    parser.add_argument(
        "-D",
        "--database",
        help="Specify the database location",
        default="/var/lib/dp3t/database.db",
    )
    parser.add_argument(
        "-i",
        "--iface",
        help="Transmit on the specified interface, not [hci]0",
        type=int,
        default=0,
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        help="Do not execute the required command(s)",
        action="store_true",
    )
    parser.add_argument(
        "-r",
        "--rssi",
        help="Specify the received signal strength indication",
        type=int,
        default=0xC0,
    )
    parser.add_argument(
        "-v", "--verbose", help="Set verbose logging", action="store_true"
    )
    args = parser.parse_args()

    # Setup logging
    global logger
    logger = logging.getLogger("beacon_tx")
    if args.debug:
        log_handler = logging.StreamHandler(sys.stderr)
    else:
        log_handler = logging.FileHandler("/var/log/beacon_tx")
    formatter = logging.Formatter("%(asctime)s: %(message)s")
    log_handler.setFormatter(formatter)

    logger.addHandler(log_handler)

    global dry_run
    dry_run = args.dry_run

    if args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logger.setLevel(log_level)
    log_handler.setLevel(log_level)

    logger.info("Starting up")

    # Transmit and store beacon packets
    current_ephid = None
    transmitter = ContactTracer(None, args.database)
    while True:
        ephid = transmitter.get_ephid_for_time(datetime.now())
        if ephid != current_ephid:
            set_transmit(f"hci{args.iface}", ephid, args.rssi)
            current_ephid = ephid
            logger.debug(f"Change ephid to {ephid.hex()}")
        # Wait for the current epoch (e.g. 15 minutes) to pass
        # Sample every minute
        time.sleep(EPOCH_LENGTH / 60)


if __name__ == "__main__":
    main()
