# Battery Management System Operation
The included battery management system (BMS) continuously monitors the battery voltage to prevent overdischarge. It automatically turns off the power supply of the RPi in case of low battery voltage. The only way to then turn it back on is to plug in the charger. It is up to the developer to regularly communicate with the BMS and shut down the RPi when required. The developer should only use the provided shutdown Python function (see Section "Raspberry - Battery Management System Communication") to turn off the RPi. 

# Raspberry Pi - Battery Management System Communication
The RPi communicates over SPI with the battery management microcontroller. The microcontroller handles the battery and acts as an RTC. In order to communicate with it a set of Python 3 functions are provided in the folder "epidose_hw_scripts".

| Function | Operation |
| ------ | ------ |
| get_battery | Returns the battery percentage.  |
| get_rtc_timedate | Returns a Python datetime object. |
| set_rtc_timedate | Sets the microcontroller's time and date to the RPi's current time and date |
| shutdown_rpi | Syncs the filesystems, instructs the microcontroller to turn off the RPi's power supply after 30s and shutdowns the RPi.|
| reboot_rpi | Syncs the filesystems, instructs the microcontroller to cycle the RPi's power supply after 30s and shutdowns the RPi.|
| get_stm_fw | Returns the microcontroller's firmware version.|

# Raspberry Pi - Battery Management System Connections
| Raspberry Pi | STM32L010F4P6	| Operation | Value on Power-Up | Comments |
| ------ | ------ | ------ | ------ | ------ |
| GPIO27 | NRST	|  | HIGH-Z  |  |
| GPIO22 | PA3	|  |  LOW |  RPi -> Input, STM32 - > Output|
| GPIO10 | PA7	| SPI MOSI  |  |  |
| GPIO9 | PA6	| SPI MISO |  |  |
| GPIO11 | PA5	| SPI CLK |  |  |
| GPIO25 | PA4	| SPI CS  | HIGH | RPi -> Master, STM32 -> Slave |
| GPIO19 | 	| STATUS LED-R | HIGH-Z |  |
| GPIO26 | 	| STATUS LED-G | HIGH-Z |  |
| GPIO20 | 	| DATA SWITCH | HIGH | External Pull-Up resistor |
| GPIO21 | PB1	| WIFI SWITCH | HIGH | External Pull-Up resistor |


# Buttons
The Epidose has three buttons. Two of them are connected to RPi's IOs (Share and WiFi) and the third one (Reset) is connected to the battery management microcontroller. Their operation is explaned below. 
| Buttton | Operation |
| ------ | ------ |
| Reset | Resets the battery management system and RPi by cycling its power supply. It should be used only in case of software failure as it may cause permanent damage to the RPi filesystem.  |
| Share | Software defined (RPi) |
| WiFi | Software defined (RPi) |

# LEDs
The Epidose has two LEDs. The "Battery" LED is connected to the battery management microcontroller and indicates the battery status while the "Status" LED is used by the Epidose software running on the Raspberry.
| Battery LED |  |
|------ | ------ |
| Blinking Red (every 10s)| Low Battery  |
| Green | Charging |

| Status LED |  |
|------ | ------ |
| RG LED | Software defined (RPi) |
