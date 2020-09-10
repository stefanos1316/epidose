#!/usr/bin/env python3

""" Test and abstract the operation of the button and the LED. """

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
from epidose.common.daemon import Daemon

# This import only works on a Rasberry Pi; ignore import when testing
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    pass
import time
import sys

# Ports with GPIO (BCM) numbering
SHARE_SWITCH_PORT = 20
WIFI_SWITCH_PORT = 21
RED_LED_PORT = 19
ORANGE_LED_PORT = 4
GREEN_LED_PORT = 26


def setup():
    """Setup GPIO for I/O
    This must be called before calling the other functions."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)


def setup_leds():
    """Setup the LED port.
    This must be called before calling the other functions."""
    setup()

    # Red external LED
    GPIO.setup(RED_LED_PORT, GPIO.OUT)
    GPIO.setup(GREEN_LED_PORT, GPIO.OUT)


def setup_switch(port):
    """Setup the specified button I/O port.
    This must be called before calling the other functions."""
    GPIO.setup(port, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def cleanup():
    """Cleanup the GPIO API."""
    GPIO.cleanup()


def wait_for_button_press(port):
    """Return when the button is pressed.
    This is interrupt-driven and therefore very efficient."""
    GPIO.wait_for_edge(port, GPIO.FALLING)


def wait_for_button_release(port):
    """Return when the button is release.
    This is interrupt-driven and therefore very efficient."""
    GPIO.wait_for_edge(port, GPIO.RISING)


def button_pressed(port):
    """ Return true if the button is pressed. """
    return not GPIO.input(port)


def red_led_set(value):
    """ Turn the LED on or off depending on the passed value. """
    # Negative logic!
    GPIO.output(RED_LED_PORT, GPIO.LOW if value else GPIO.HIGH)


def green_led_set(value):
    """ Turn the LED on or off depending on the passed value. """
    GPIO.output(GREEN_LED_PORT, GPIO.LOW if value else GPIO.HIGH)


def orange_led_set(value):
    """ Turn the LED on or off depending on the passed value. """
    if value:
        GPIO.output(GREEN_LED_PORT, GPIO.LOW)
        GPIO.output(RED_LED_PORT, GPIO.LOW)
    else:
        GPIO.output(GREEN_LED_PORT, GPIO.HIGH)
        GPIO.output(RED_LED_PORT, GPIO.HIGH)


def toggle(led_state, switch):
    """ Toggle the LED with each key press. """
    print("To terminate, press ^C and then the button.")
    wait_for_button_press(switch)
    red_led_set(led_state)
    green_led_set(led_state)
    print(f"{time.time()}: Button Pressed")
    # Debounce
    time.sleep(0.2)
    return not led_state


def main():
    parser = argparse.ArgumentParser(description="Contact tracing device I/O")
    parser.add_argument(
        "-d", "--debug", help="Run in debug mode logging to stderr", action="store_true"
    )
    parser.add_argument("-G", "--green-on", help="Turn red LED on", action="store_true")
    parser.add_argument(
        "-g", "--green-off", help="Turn red LED off", action="store_true"
    )
    parser.add_argument(
        "-O", "--orange-on", help="Turn orange LED on", action="store_true"
    )
    parser.add_argument(
        "-o", "--orange-off", help="Turn orange LED off", action="store_true"
    )
    parser.add_argument("-R", "--red-on", help="Turn red LED on", action="store_true")
    parser.add_argument("-r", "--red-off", help="Turn red LED off", action="store_true")
    parser.add_argument(
        "-s", "--share-wait", help="Wait for share key press", action="store_true"
    )
    parser.add_argument(
        "-t", "--test", help="Toggle LED with button", action="store_true"
    )
    parser.add_argument(
        "-v", "--verbose", help="Set verbose logging", action="store_true"
    )
    parser.add_argument(
        "-w", "--wifi-wait", help="Wait for WiFi key press", action="store_true"
    )
    args = parser.parse_args()

    # Setup logging
    daemon = Daemon("device_io", args)
    global logger
    logger = daemon.get_logger()

    if args.test:
        setup_leds()
        setup_switch(SHARE_SWITCH_PORT)
        setup_switch(WIFI_SWITCH_PORT)
        led_state = True
        while True:
            try:
                print("Press the share button to toggle the LED.")
                led_state = toggle(led_state, SHARE_SWITCH_PORT)
                print("Press the WiFi button to toggle the LED.")
                led_state = toggle(led_state, WIFI_SWITCH_PORT)
            except KeyboardInterrupt:
                sys.exit(0)
    if args.green_off:
        logger.debug("Turn green LED off")
        setup_leds()
        green_led_set(False)
    if args.green_on:
        logger.debug("Turn green LED on")
        setup_leds()
        green_led_set(True)
    if args.orange_off:
        logger.debug("Turn orange LED off")
        setup_leds()
        orange_led_set(False)
    if args.orange_on:
        logger.debug("Turn orange LED on")
        setup_leds()
        orange_led_set(True)
    if args.red_off:
        logger.debug("Turn red LED off")
        setup_leds()
        red_led_set(False)
    if args.red_on:
        logger.debug("Turn red LED on")
        setup_leds()
        red_led_set(True)
    if args.share_wait:
        logger.debug("Waiting for share button press; press ^C and button to abort")
        setup()
        setup_switch(SHARE_SWITCH_PORT)
        wait_for_button_press(SHARE_SWITCH_PORT)
        logger.debug("Share button pressed")

    if args.wifi_wait:
        logger.debug("Waiting for WiFi button press; press ^C and button to abort")
        setup()
        setup_switch(WIFI_SWITCH_PORT)
        wait_for_button_press(WIFI_SWITCH_PORT)
        logger.debug("WiFi button pressed")


if __name__ == "__main__":
    main()
