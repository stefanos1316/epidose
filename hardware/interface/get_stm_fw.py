#!/usr/bin/python3

#Copyright 2020 Konstantinos Papafotis, Konstantinos Asimakopoulos, Paul P. Sotiriadis
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

import sys
import time
import spidev


def get_stm_fw():
	try:
		spi = spidev.SpiDev()
		spi.open(0,0)

# Set SPI speed and mode
		spi.max_speed_hz = 5000
		spi.mode = 0
		spi.cshigh = True
# ask for fw version
		msg = [9,0,0,0]
		spi.writebytes(msg)
#actually get it
		time.sleep(0.001)
		result=spi.readbytes(4)
		return (result[0]+result[1]*0.1)
		spi.close()
	except:
		print("Unexpected error:", sys.exc_info()[0])
		return 0
