EESchema Schematic File Version 4
LIBS:circuit-cache
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title "Epidose: Raspberry Pi contact tracing"
Date "2020-06-09"
Rev "2.0"
Comp "Author: Diomidis Spinellis"
Comment1 "License: CC-BY"
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Device:Battery_Cell BT1
U 1 1 5EDF22CD
P 4200 4450
F 0 "BT1" H 4318 4546 50  0000 L CNN
F 1 "18650 3.7V - 3500mAh" H 4318 4455 50  0000 L CNN
F 2 "" V 4200 4510 50  0001 C CNN
F 3 "~" V 4200 4510 50  0001 C CNN
	1    4200 4450
	1    0    0    -1  
$EndComp
$Comp
L Connector:Raspberry_Pi_2_3 J1
U 1 1 5EE0BA77
P 7800 3800
F 0 "J1" H 7800 5281 50  0000 C CNN
F 1 "Raspberry Pi Zero-W" H 7800 5190 50  0000 C CNN
F 2 "" H 7800 3800 50  0001 C CNN
F 3 "https://www.raspberrypi.org/documentation/hardware/raspberrypi/schematics/rpi_SCH_3bplus_1p0_reduced.pdf" H 7800 3800 50  0001 C CNN
	1    7800 3800
	1    0    0    -1  
$EndComp
Wire Wire Line
	7700 5250 7700 5100
$Comp
L Switch:SW_SPST SW1
U 1 1 5EC5601D
P 6400 3000
F 0 "SW1" H 6400 3235 50  0000 C CNN
F 1 "SW_SPST momentary press" H 6400 3144 50  0000 C CNN
F 2 "" H 6400 3000 50  0001 C CNN
F 3 "~" H 6400 3000 50  0001 C CNN
	1    6400 3000
	1    0    0    -1  
$EndComp
$Comp
L LED:IR204A D1
U 1 1 5EC54C71
P 6650 3800
F 0 "D1" H 6600 4090 50  0000 C CNN
F 1 "Mini LED; red" H 6600 3999 50  0000 C CNN
F 2 "LED_THT:LED_D3.0mm_IRBlack" H 6650 3975 50  0001 C CNN
F 3 "" H 6600 3800 50  0001 C CNN
	1    6650 3800
	1    0    0    -1  
$EndComp
Wire Wire Line
	7000 3800 6750 3800
Wire Wire Line
	6750 3800 6550 3800
Connection ~ 6750 3800
$Comp
L Device:R R1
U 1 1 5EC5713D
P 6450 4200
F 0 "R1" V 6243 4200 50  0000 C CNN
F 1 "330Ω" V 6334 4200 50  0000 C CNN
F 2 "" V 6380 4200 50  0001 C CNN
F 3 "~" H 6450 4200 50  0001 C CNN
	1    6450 4200
	1    0    0    -1  
$EndComp
Wire Wire Line
	7000 3000 6600 3000
Wire Wire Line
	6450 3800 6450 4050
Wire Wire Line
	6450 4350 6450 5250
Wire Wire Line
	6450 5250 7700 5250
Wire Wire Line
	6200 3000 6100 3000
Wire Wire Line
	6100 5450 7600 5450
Wire Wire Line
	7600 5450 7600 5100
Wire Wire Line
	6100 3000 6100 5450
$Comp
L Regulator_Switching:TSR_1-2415 U1
U 1 1 5EE1E07D
P 5350 3950
F 0 "U1" H 5350 4317 50  0000 C CNN
F 1 "5V 2A buck converter" H 5350 4226 50  0000 C CNN
F 2 "Converter_DCDC:Converter_DCDC_TRACO_TSR-1_THT" H 5350 3800 50  0001 L CIN
F 3 "http://www.tracopower.com/products/tsr1.pdf" H 5350 3950 50  0001 C CNN
	1    5350 3950
	1    0    0    -1  
$EndComp
Wire Wire Line
	4200 4250 4200 3850
Wire Wire Line
	4200 3850 4950 3850
Wire Wire Line
	5750 3850 5850 3850
Wire Wire Line
	5850 3850 5850 2300
Wire Wire Line
	5850 2300 7600 2300
Wire Wire Line
	7600 2300 7600 2500
Wire Wire Line
	5350 4150 5350 4850
Wire Wire Line
	5350 5650 7800 5650
Wire Wire Line
	7800 5650 7800 5100
Wire Wire Line
	4200 4550 4200 4850
Wire Wire Line
	4200 4850 5350 4850
Connection ~ 5350 4850
Wire Wire Line
	5350 4850 5350 5650
$Comp
L Battery_Management:MCP73832-2-OT U2
U 1 1 5EE25348
P 3200 3950
F 0 "U2" H 3200 4431 50  0000 C CNN
F 1 "Battery charger module" H 3200 4340 50  0000 C CNN
F 2 "Package_TO_SOT_SMD:SOT-23-5" H 3250 3700 50  0001 L CIN
F 3 "http://ww1.microchip.com/downloads/en/DeviceDoc/20001984g.pdf" H 3050 3900 50  0001 C CNN
	1    3200 3950
	1    0    0    -1  
$EndComp
Wire Wire Line
	3600 3850 4200 3850
Connection ~ 4200 3850
Wire Wire Line
	3200 4850 4200 4850
Wire Wire Line
	3200 4250 3200 4850
Connection ~ 4200 4850
$Comp
L Connector:USB_B_Micro J2
U 1 1 5EE27A76
P 3000 2850
F 0 "J2" V 3011 3180 50  0000 L CNN
F 1 "USB_B_Micro" V 3102 3180 50  0000 L CNN
F 2 "" H 3150 2800 50  0001 C CNN
F 3 "~" H 3150 2800 50  0001 C CNN
	1    3000 2850
	0    1    1    0   
$EndComp
Wire Wire Line
	3200 3650 3200 3150
Wire Wire Line
	2600 2850 2500 2850
Wire Wire Line
	2500 2850 2500 4850
Wire Wire Line
	2500 4850 3200 4850
Connection ~ 3200 4850
$EndSCHEMATC
