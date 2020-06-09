#!/usr/bin/env python3

""" A sleep function that can be detectably interrupted """

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

from threading import Event
import signal


class InterruptibleSleep:
    """ Provide a sleep-like function that can be interrupted and
    by a detectable signal.  See https://stackoverflow.com/a/46346184/20520
    """

    def __init__(self, signals):
        """ Create an object for the specified signals """
        for s in signals:
            signal.signal(s, self.sig_handler)
        self.event = Event()
        self.signaled = False

    def sleep(self, t):
        """ Sleep for the specified time interval, or less if the signal
        is received.  The "signaled" member can be examined to see if a
        signal was received, while sleeping. """
        self.event.clear()
        self.signaled = False
        self.event.wait(t)

    def sig_handler(self, signum, frame):
        self.signaled = True
        self.event.set()


def main():
    sleeper = InterruptibleSleep([signal.SIGTERM])
    print("Expect to see a 'signaled' message when you send a TERM signal")
    while True:
        print("Sleeping")
        sleeper.sleep(5)
        if sleeper.signaled:
            print("Signaled")
        print("Looping")


if __name__ == "__main__":
    main()
