#!/usr/bin/env python3

""" Test and abstract the operation of the switch and the LED. """

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
from epidose.common import logging
import RPi.GPIO as GPIO
import time

SWITCH_PORT = 15
LED_PORT = 21


def setup():
    """ Setup the LED and switch I/O ports.
    This must be called before calling the other functions."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(SWITCH_PORT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(LED_PORT, GPIO.OUT)


def wait_for_switch_press():
    """ Return when the switch is pressed.
    This is interrupt-driven and therefore very efficient. """
    GPIO.wait_for_edge(SWITCH_PORT, GPIO.FALLING)


def wait_for_switch_release():
    """ Return when the switch is release.
    This is interrupt-driven and therefore very efficient. """
    GPIO.wait_for_edge(SWITCH_PORT, GPIO.RISING)


def switch_pressed():
    """ Return true if the switch is pressed. """
    return not GPIO.input(SWITCH_PORT)


def led_set(value):
    """ Turn the LED on or off depending on the passed value. """
    if value:
        GPIO.output(LED_PORT, GPIO.HIGH)
    else:
        GPIO.output(LED_PORT, GPIO.LOW)


def toggle():
    """ Toggle the LED with each key press. """
    led_state = True
    print("Press the button to toggle the LED.")
    print("To terminate, press ^C and then the button.")
    while True:
        wait_for_switch_press()
        led_set(led_state)
        print(f"{time.time()}: Button Pressed")
        # Debounce
        time.sleep(0.2)
        led_state = not led_state


def main():
    parser = argparse.ArgumentParser(description="Contact tracing device I/O")
    parser.add_argument("-1", "--on", help="Turn LED on", action="store_true")
    parser.add_argument("-0", "--off", help="Turn LED off", action="store_true")
    parser.add_argument(
        "-d", "--debug", help="Run in debug mode logging to stderr", action="store_true"
    )
    parser.add_argument("-l", "--led", help="Turn LED on or off", type=int)
    parser.add_argument(
        "-t", "--test", help="Toggle LED with switch", action="store_true"
    )
    parser.add_argument(
        "-v", "--verbose", help="Set verbose logging", action="store_true"
    )
    parser.add_argument("-w", "--wait", help="Wait for key press", action="store_true")
    args = parser.parse_args()

    # Setup logging
    global logger
    logger = logging.getLogger("device_io", args)

    setup()
    if args.test:
        toggle()
    elif args.off:
        logger.debug("Turn LED off")
        led_set(False)
    elif args.on:
        logger.debug("Turn LED on")
        led_set(True)
    elif args.wait:
        logger.debug("Waiting for key press")
        wait_for_switch_press()
        logger.debug("Key pressed")
        # Debounce
        time.sleep(0.2)


if __name__ == "__main__":
    main()
