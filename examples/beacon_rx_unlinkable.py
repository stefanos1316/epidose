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
import bluetooth._bluetooth as bluez
from dp3t.config import EPOCH_LENGTH
from datetime import datetime
from dp3t.protocols.unlinkable_db import ContactTracer
import logging
import subprocess
import struct
import sys
import time

OGF_LE_CTL = 0x08
OCF_LE_SET_SCAN_ENABLE = 0x000C

def set_receive(socket):
    """Setup to receive contact tracing packets."""
    # Enable scanning
    enable_scanning = struct.pack("<BB", 0x01, 0x00)
    bluez.hci_send_cmd(socket, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE,
                       enable_scanning)

    # Obtain Bluetooth advertisement packets
    old_filter = socket.getsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, 14)
    listen_filter = bluez.hci_filter_new()
    bluez.hci_filter_all_events(listen_filter)
    bluez.hci_filter_set_ptype(listen_filter, bluez.HCI_EVENT_PKT)
    socket.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, listen_filter)


def unpack_byte(b):
    """Return b unpacked from a byte value"""
    return struct.unpack("b", bytes([b]))

def process_packet(socket):
    """Read and process a single broadcast packet."""
    packet = socket.recv(255)
    packet_length, = unpack_byte(packet[2])
    if (packet_length != 42 or
            packet[17:18] != bytes([0x1b]) or
            packet[21:23] != bytes([0xbe, 0xac]) or
            packet[23:25] != bytes([0xed, 0x05]) or
            packet[25:26] != bytes([1]) or
            packet[26:27] != bytes([1])):
        return
    # This is a contact tracing packet
    ephid = packet[27:43]
    rssi, = unpack_byte(packet[-1])
    logger.info(f"Got ephid {ephid.hex()} RSSI {rssi}")


def main():
    parser = argparse.ArgumentParser(description="Contact tracing beacon receiver")
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
        help="Listen on the specified interface number, not [hci]0",
        type=int,
        default=0,
    )
    parser.add_argument(
        "-v", "--verbose", help="Set verbose logging", action="store_true"
    )
    args = parser.parse_args()

    global logger
    logger = logging.getLogger("beacon_rx")
    if args.debug:
        log_handler = logging.StreamHandler(sys.stderr)
    else:
        log_handler = logging.FileHandler("/var/log/beacon_rx")
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

    try:
        socket = bluez.hci_open_dev(args.iface)
        set_receive(socket)
        while True:
            process_packet(socket)
    except Exception as e:
        logger.error("Error accessing Bluetooth: " + e)

if __name__ == "__main__":
    main()
