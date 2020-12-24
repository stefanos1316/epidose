#!/usr/bin/python3

# Copyright 2020 Konstantinos Papafotis, Konstantinos Asimakopoulos, Paul P. Sotiriadis
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
from time import sleep
import spidev
from datetime import datetime


def rtc_fix_result_padding(_res):
    if _res < 10:
        return "0" + str(_res)
    else:
        return str(_res)


def get_rtc_timedate():
    try:
        spi = spidev.SpiDev()
        spi.open(0, 0)

        # Set SPI speed and mode
        spi.max_speed_hz = 5000
        # spi.mode = 0
        spi.cshigh = True
        # ask for time
        msg = [2, 0, 0, 0]
        spi.writebytes(msg)
        # actually get it
        sleep(0.001)
        result = spi.readbytes(4)
        time_str = (
            rtc_fix_result_padding(result[0])
            + rtc_fix_result_padding(result[1])
            + rtc_fix_result_padding(result[2])
        )
        print(result)

        # ask for date
        msg = [3, 0, 0, 0]
        spi.writebytes(msg)
        # actually get it
        sleep(0.001)
        result = spi.readbytes(4)
        date_str = (
            rtc_fix_result_padding(result[0])
            + rtc_fix_result_padding(result[1])
            + rtc_fix_result_padding(result[2] - 4)
        )
        print(result)

        spi.close()
        # create the datetime object
        date_time_obj = datetime.strptime(
            str(date_str + " " + time_str), "%d%m%y %H%M%S"
        )
        return date_time_obj
    except Exception:
        print("Unexpected error:", sys.exc_info()[0])
        return 0


if __name__ == "__main__":
    print(get_rtc_timedate())
