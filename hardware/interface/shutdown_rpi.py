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
import os

def shutdown_rpi():
	try:

		spi = spidev.SpiDev()
		spi.open(0,0)

# Set SPI speed and mode
		spi.max_speed_hz = 50000
#spi.mode = 0
		spi.cshigh = True
# reboot
		msg = [6,0,0,0]
		os.system('sync')

		fake=spi.xfer2(msg)
		spi.close()
		os.system('sudo shutdown now')
	except:
		print("Unexpected error:", sys.exc_info()[0])

shutdown_rpi()
