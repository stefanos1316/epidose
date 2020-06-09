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

SWITCH_PORT = 15
LED_PORT = 21


def setup():
    """ Setup GPIO for I/O
    This must be called before calling the other functions."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)


def setup_leds():
    """ Setup the LED port.
    This must be called before calling the other functions."""
    setup()

    # Red external LED
    GPIO.setup(LED_PORT, GPIO.OUT)

    # Green on-board LED
    with open("/sys/class/leds/led0/trigger", "w") as f:
        f.write("none")


def setup_switch():
    """ Setup the button I/O port.
    This must be called before calling the other functions."""
    setup()

    GPIO.setup(SWITCH_PORT, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def cleanup():
    """Cleanup the GPIO API."""
    GPIO.cleanup()
    with open("/sys/class/leds/led0/trigger", "w") as f:
        f.write("mmc0")


def wait_for_button_press():
    """ Return when the button is pressed.
    This is interrupt-driven and therefore very efficient. """
    GPIO.wait_for_edge(SWITCH_PORT, GPIO.FALLING)


def wait_for_button_release():
    """ Return when the button is release.
    This is interrupt-driven and therefore very efficient. """
    GPIO.wait_for_edge(SWITCH_PORT, GPIO.RISING)


def button_pressed():
    """ Return true if the button is pressed. """
    return not GPIO.input(SWITCH_PORT)


def red_led_set(value):
    """ Turn the LED on or off depending on the passed value. """
    GPIO.output(LED_PORT, GPIO.HIGH if value else GPIO.LOW)


def green_led_set(value):
    """ Turn the LED on or off depending on the passed value. """
    with open("/sys/class/leds/led0/brightness", "w") as f:
        f.write("0" if value else "1")


def toggle():
    """ Toggle the LED with each key press. """
    led_state = True
    print("Press the button to toggle the LED.")
    print("To terminate, press ^C and then the button.")
    while True:
        wait_for_button_press()
        red_led_set(led_state)
        green_led_set(not led_state)
        print(f"{time.time()}: Button Pressed")
        # Debounce
        time.sleep(0.2)
        led_state = not led_state


def main():
    parser = argparse.ArgumentParser(description="Contact tracing device I/O")
    parser.add_argument(
        "-d", "--debug", help="Run in debug mode logging to stderr", action="store_true"
    )
    parser.add_argument("-G", "--green-on", help="Turn red LED on", action="store_true")
    parser.add_argument(
        "-g", "--green-off", help="Turn red LED off", action="store_true"
    )
    parser.add_argument("-R", "--red-on", help="Turn red LED on", action="store_true")
    parser.add_argument("-r", "--red-off", help="Turn red LED off", action="store_true")
    parser.add_argument(
        "-t", "--test", help="Toggle LED with button", action="store_true"
    )
    parser.add_argument(
        "-v", "--verbose", help="Set verbose logging", action="store_true"
    )
    parser.add_argument("-w", "--wait", help="Wait for key press", action="store_true")
    args = parser.parse_args()

    # Setup logging
    daemon = Daemon("device_io", args)
    global logger
    logger = daemon.get_logger()

    if args.test:
        setup_leds()
        setup_switch()
        try:
            toggle()
        except KeyboardInterrupt:
            pass
    if args.green_off:
        logger.debug("Turn green LED off")
        setup_leds()
        green_led_set(False)
    if args.green_on:
        logger.debug("Turn green LED on")
        setup_leds()
        green_led_set(True)
    if args.red_off:
        logger.debug("Turn red LED off")
        setup_leds()
        red_led_set(False)
    if args.red_on:
        logger.debug("Turn red LED on")
        setup_leds()
        red_led_set(True)
    if args.wait:
        logger.debug("Waiting for button press; press ^C and button to abort")
        setup_switch()
        wait_for_button_press()
        logger.debug("Button pressed")
    # Wait for LEDs to be visible
    time.sleep(1)
    cleanup()


if __name__ == "__main__":
    main()
