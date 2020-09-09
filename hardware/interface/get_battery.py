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


def get_battery():
	voltage_percent=[[3.4000,0],[3.4100,1.4888],[3.4200,2.9776],[3.4300,4.4664],[3.4400,5.9552],[3.4500,7.4440],[3.4600,8.9328],[3.4700,10.4216],[3.4800,11.9104],[3.4900,13.3992],[3.5000,14.8880],[3.5100,16.3768],[3.5200,17.8656],[3.5300,19.3544],[3.5400,20.8432],[3.5500,22.3320],[3.5600,23.8208],[3.5700,25.3096],[3.5800,26.7984],[3.5900,28.2872],[3.6000,29.7760],[3.6100,31.2648],[3.6200,32.7536],[3.6300,34.2424],[3.6400,35.7312],[3.6500,37.2200],[3.6600,38.7088],[3.6700,40.1976],[3.6800,41.6864],[3.6900,43.1752],[3.7000,44.6640],[3.7100,46.1528],[3.7200,47.6416],[3.7300,49.1304],[3.7400,50.6192],[3.7500,52.1080],[3.7600,53.5968],[3.7700,55.0856],[3.7800,56.5744],[3.7900,58.0632],[3.8000,59.5520],[3.8100,61.0408],[3.8200,62.5296],[3.8300,64.0184],[3.8400,65.5072],[3.8500,66.9960],[3.8600,68.4848],[3.8700,69.9736],[3.8800,71.4624],[3.8900,72.9512],[3.9000,74.4400],[3.9100,75.9288],[3.9200,77.4176],[3.9300,78.9064],[3.9400,80.3952],[3.9500,81.8840],[3.9600,83.3728],[3.9700,84.8616],[3.9800,86.3504],[3.9900,87.8392],[4.0000,89.3280],[4.0100,90.8168],[4.0200,92.3056],[4.0300,93.7944],[4.0400,95.2832],[4.0500,96.7720],[4.0600,98.2608],[4.0700,99.7496],[4.0800,100.0000]]

	try:
		spi = spidev.SpiDev()
		spi.open(0,0)

# Set SPI speed and mode
		spi.max_speed_hz = 50000
#spi.mode = 0
		spi.cshigh = True
# ask for battery voltage
		msg = [1,0,0,0]
		fake=spi.xfer2(msg)
#actually get it
		msg = [0,0,0,0]
		result=spi.xfer2(msg)
		temp=(result[0]<<8)|result[1]
		voltage=2*(3.258*temp)/(4096)
		spi.close()
	except:
		print("Unexpected error:", sys.exc_info()[0])
		return 0

	prev_error=10000
	for idx, val in enumerate(voltage_percent):
		if (abs(val[0]-voltage)<=prev_error):
			prev_error=abs(val[0]-voltage)
		else:
			return (voltage_percent[idx-1][1])
			break

