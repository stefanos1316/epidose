#!/usr/bin/env python3

""" Contact tracing beacon format """

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

# Start of a BLE transmission command or received packet
# This is defined in the Bluetoth Core Specification V4.0
# page 1062 and in the Apple/Google Contact Tracing Bluetooth
# specification.
BLE_PACKET = bytes([
        0x1c,  # Number of significant octets in advertising data
        0x02,  # Flags: Length
        0x01,  # Flags: Type Flag
        0x1A,  # Flags: Value (0x02 is LE general discoverable)
        0x03,  # ServiceUUID: Length
        0x03,  # ServiceUUID: Type (Complete 16-bit ServiceUUID)
        0x6f,  # ServiceUUID: Contact Detection Service (0xFD6F)
        0xfd,  # ServiceUUID: Contact Detection Service (0xFD6F)
        0x13,  # Service Data: Length
        0x16,  # Service Data: Type (16 byte UUID)
        0x6f,  # Service Data: Contact Detection Service (0xFD6F)
        0xfd,  # Service Data: Contact Detection Service (0xFD6F)
])
