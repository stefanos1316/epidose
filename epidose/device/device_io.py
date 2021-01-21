#!/usr/bin/env python3

""" Test and abstract the operation of the button and the LED. """

__copyright__ = """
    Copyright 2020 Diomidis Spinellis, Konstantinos Papafotis,
      Konstantinos Asimakopoulos, and Paul P. Sotiriadis

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
from datetime import datetime
from pathlib import Path

# This import only works on a Rasberry Pi; ignore import when testing
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    pass
import spidev
import sys
import time

# Ports with GPIO (BCM) numbering
SHARE_SWITCH_PORT = 20
WIFI_SWITCH_PORT = 21
RED_LED_PORT = 19
ORANGE_LED_PORT = 4
GREEN_LED_PORT = 26

# Touched on every LED status change
# Located on /run, which is mounted on tmpfs, to avoid SSD wear
LED_CHANGE = Path("/run/epidose-led-change")


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
    LED_CHANGE.touch()
    # Negative logic!
    GPIO.output(RED_LED_PORT, GPIO.LOW if value else GPIO.HIGH)


def green_led_set(value):
    """ Turn the LED on or off depending on the passed value. """
    LED_CHANGE.touch()
    GPIO.output(GREEN_LED_PORT, GPIO.LOW if value else GPIO.HIGH)


def orange_led_set(value):
    """ Turn the LED on or off depending on the passed value. """
    LED_CHANGE.touch()
    if value:
        GPIO.output(GREEN_LED_PORT, GPIO.LOW)
        GPIO.output(RED_LED_PORT, GPIO.LOW)
    else:
        GPIO.output(GREEN_LED_PORT, GPIO.HIGH)
        GPIO.output(RED_LED_PORT, GPIO.HIGH)


def led_change_age():
    """ Return the time elapsed from the last LED modification """
    return datetime.now().timestamp() - LED_CHANGE.stat().st_mtime


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


def spi_setup():
    """ Return an spi handle after setting it up for communication """
    spi = spidev.SpiDev()
    spi.open(0, 0)

    # Set SPI speed and mode
    spi.max_speed_hz = 5000
    spi.mode = 0
    spi.cshigh = True
    return spi


def spi_command(spi, message, get_result):
    """Write the specified message to the serial peripheral interface
    and return the result if get_result is true."""
    spi.writebytes(message)
    time.sleep(0.001)
    return spi.readbytes(4) if get_result else None


def get_battery_voltage():
    """ Return the battery's voltage in V"""
    spi = spi_setup()
    # Ask for battery voltage
    result = spi_command(spi, [1, 0, 0, 0], True)
    value = (result[0] << 8) | result[1]
    voltage = 2 * (3.258 * value) / 4096
    spi.close()
    return voltage


def zero_pad(v):
    """ Return value as a string zero-padded to two digits"""
    if v < 10:
        return "0" + str(v)
    else:
        return str(v)


def get_real_time_clock():
    """Return a datetime object obtained from the controller's
    real time clock"""

    spi = spi_setup()
    # Ask for time
    result = spi_command(spi, [2, 0, 0, 0], True)
    time_str = zero_pad(result[0]) + zero_pad(result[1]) + zero_pad(result[2])

    # Ask for date
    result = spi_command(spi, [3, 0, 0, 0], True)
    date_str = zero_pad(result[0]) + zero_pad(result[1]) + zero_pad(result[2] - 4)
    spi.close()

    # Create the datetime object
    date_time_obj = datetime.strptime(str(date_str + " " + time_str), "%d%m%y %H%M%S")
    return date_time_obj


def set_real_time_clock():
    # Datetime object containing current date and time
    now = datetime.now()

    spi = spi_setup()
    # Set time to now
    spi_command(spi, [4, now.hour, now.minute, now.second], False)

    # Set day to today
    spi_command(spi, [5, now.day, now.month, now.year - 2000], False)
    spi.close()


def schedule_power_off():
    """Schedule the power to be shut down after 30s"""
    spi = spi_setup()
    spi_command(spi, [6, 0, 0, 0], False)
    spi.close()


def main():
    parser = argparse.ArgumentParser(description="Contact tracing device I/O")
    parser.add_argument(
        "-b", "--battery", help="Display battery voltage", action="store_true"
    )
    parser.add_argument(
        "-c", "--clock-get", help="Display real time clock", action="store_true"
    )
    parser.add_argument(
        "-C",
        "--clock-set",
        help="Set real time clock to the current time",
        action="store_true",
    )
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
    parser.add_argument(
        "-p", "--power-off", help="Schedule power to turn off", action="store_true"
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

    if args.battery:
        print(get_battery_voltage())
    if args.test:
        print(get_real_time_clock())
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

    if args.clock_get:
        print(get_real_time_clock())
    if args.clock_set:
        set_real_time_clock()
        print(get_real_time_clock())

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
    if args.power_off:
        logger.debug("Schedule power off")
        schedule_power_off()
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
