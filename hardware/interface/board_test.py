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

from gpiozero import LED
from gpiozero import Button
from time import sleep
import spidev
from get_battery import *
from get_stm_fw import get_stm_fw
from set_rtc_timedate import set_rtc_timedate
from get_rtc_timedate import get_rtc_timedate


button_test=0

def stm32_gpio_test():
	try:
        	spi = spidev.SpiDev()
        	spi.open(0,0)
# Set SPI speed and mode
        	spi.max_speed_hz = 50000
#spi.mode = 0
        	spi.cshigh = True
# ask for test mode
        	msg = [8,0,0,0]
        	fake=spi.xfer2(msg)
        	spi.close()
	except:
        	print("Unexpected error:", sys.exc_info()[0])



#################################################
def print_data():
    print("Data Switch Pressed")
    stm32_gpio_test()
    global button_test
    button_test=button_test+1

def print_wifi():
    print("WiFi Switch Pressed")
    stm32_gpio_test()
    global button_test
    button_test=button_test+1

led_r = LED(19)
led_g = LED(26)
data_sw = Button(20)
wifi_sw = Button(21)

print("Board Tester")

print("STM32 Firmware Version:"+str(get_stm_fw()))
print("Battery level:"+str(get_battery())+"%")
print("Setting time...")
set_rtc_timedate()
print("Time now:"+str(get_rtc_timedate()))
print("Sleeping...")
time.sleep(2)
print("Time now:"+str(get_rtc_timedate()))

print("Press each button and check LEDs at the same time")

data_sw.when_pressed = print_data
wifi_sw.when_pressed = print_wifi

try:
	while True:
		led_r.on()
		led_g.off()
		sleep(0.5)
		led_r.off()
		led_g.on()
		sleep(0.5)
		if (button_test>=2):
			print("Test successful")
			break
except (KeyboardInterrupt, SystemExit):
	print("EXIT")
