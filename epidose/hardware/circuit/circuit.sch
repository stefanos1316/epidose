EESchema Schematic File Version 4
LIBS:circuit-cache
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title "Epidose: Raspberry Pi contact tracing"
Date "2020-07-02"
Rev "3.0"
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
$Comp
L Switch:SW_SPST SW1
U 1 1 5EC5601D
P 6350 4400
F 0 "SW1" H 6350 4635 50  0000 C CNN
F 1 "SW_SPST momentary press" H 6350 4544 50  0000 C CNN
F 2 "" H 6350 4400 50  0001 C CNN
F 3 "~" H 6350 4400 50  0001 C CNN
	1    6350 4400
	1    0    0    -1  
$EndComp
$Comp
L LED:IR204A D1
U 1 1 5EC54C71
P 6700 3300
F 0 "D1" H 6650 3590 50  0000 C CNN
F 1 "Mini LED; red" H 6650 3499 50  0000 C CNN
F 2 "LED_THT:LED_D3.0mm_IRBlack" H 6700 3475 50  0001 C CNN
F 3 "" H 6650 3300 50  0001 C CNN
	1    6700 3300
	1    0    0    -1  
$EndComp
$Comp
L Device:R R3
U 1 1 5EC5713D
P 9650 3500
F 0 "R3" V 9443 3500 50  0000 C CNN
F 1 "330Ω" V 9534 3500 50  0000 C CNN
F 2 "" V 9580 3500 50  0001 C CNN
F 3 "~" H 9650 3500 50  0001 C CNN
	1    9650 3500
	0    1    1    0   
$EndComp
$Comp
L Regulator_Switching:TSR_1-2415 U1
U 1 1 5EE1E07D
P 5350 3950
F 0 "U1" H 5350 4317 50  0000 C CNN
F 1 "Step up conv. (B6289i)" H 5350 4226 50  0000 C CNN
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
	5350 4150 5350 4400
Wire Wire Line
	4200 4550 4200 4850
Wire Wire Line
	4200 4850 5350 4850
$Comp
L Battery_Management:MCP73832-2-OT U2
U 1 1 5EE25348
P 3200 3950
F 0 "U2" H 3200 4431 50  0000 C CNN
F 1 "Battery charger (LTC4056)" H 3200 4340 50  0000 C CNN
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
$Comp
L LED:IR204A D3
U 1 1 5EFE9B29
P 9050 3500
F 0 "D3" H 9000 3790 50  0000 C CNN
F 1 "Mini LED; orange" H 9000 3699 50  0000 C CNN
F 2 "LED_THT:LED_D3.0mm_IRBlack" H 9050 3675 50  0001 C CNN
F 3 "" H 9000 3500 50  0001 C CNN
	1    9050 3500
	-1   0    0    1   
$EndComp
$Comp
L Device:R R2
U 1 1 5EFE9B2F
P 9650 3200
F 0 "R2" V 9443 3200 50  0000 C CNN
F 1 "330Ω" V 9534 3200 50  0000 C CNN
F 2 "" V 9580 3200 50  0001 C CNN
F 3 "~" H 9650 3200 50  0001 C CNN
	1    9650 3200
	0    1    1    0   
$EndComp
$Comp
L Device:R R1
U 1 1 5EFEB41B
P 6250 3300
F 0 "R1" V 6043 3300 50  0000 C CNN
F 1 "330Ω" V 6134 3300 50  0000 C CNN
F 2 "" V 6180 3300 50  0001 C CNN
F 3 "~" H 6250 3300 50  0001 C CNN
	1    6250 3300
	0    -1   -1   0   
$EndComp
$Comp
L LED:IR204A D?
U 1 1 5EFEB415
P 9050 3200
F 0 "D?" H 9000 3490 50  0000 C CNN
F 1 "Mini LED; green" H 9000 3399 50  0000 C CNN
F 2 "LED_THT:LED_D3.0mm_IRBlack" H 9050 3375 50  0001 C CNN
F 3 "" H 9000 3200 50  0001 C CNN
	1    9050 3200
	-1   0    0    1   
$EndComp
Wire Wire Line
	8600 3200 8950 3200
$Comp
L power:GND #PWR?
U 1 1 5EFF21C3
P 9950 3800
F 0 "#PWR?" H 9950 3550 50  0001 C CNN
F 1 "GND" H 9955 3627 50  0000 C CNN
F 2 "" H 9950 3800 50  0001 C CNN
F 3 "" H 9950 3800 50  0001 C CNN
	1    9950 3800
	1    0    0    -1  
$EndComp
Connection ~ 5350 4400
Wire Wire Line
	5350 4400 5350 4850
$Comp
L power:GND #PWR?
U 1 1 5EFF40C0
P 7800 5300
F 0 "#PWR?" H 7800 5050 50  0001 C CNN
F 1 "GND" H 7805 5127 50  0000 C CNN
F 2 "" H 7800 5300 50  0001 C CNN
F 3 "" H 7800 5300 50  0001 C CNN
	1    7800 5300
	1    0    0    -1  
$EndComp
Wire Wire Line
	7700 2300 7700 2500
Wire Wire Line
	5850 2300 7700 2300
Wire Wire Line
	7800 5100 7800 5300
Wire Wire Line
	5350 4850 5350 5050
Connection ~ 5350 4850
$Comp
L power:GND #PWR?
U 1 1 5EFF7797
P 5350 5050
F 0 "#PWR?" H 5350 4800 50  0001 C CNN
F 1 "GND" H 5355 4877 50  0000 C CNN
F 2 "" H 5350 5050 50  0001 C CNN
F 3 "" H 5350 5050 50  0001 C CNN
	1    5350 5050
	1    0    0    -1  
$EndComp
Wire Notes Line
	2400 2500 2400 4250
Wire Notes Line
	2400 4250 5800 4250
Wire Notes Line
	5800 4250 5800 2500
Wire Notes Line
	5800 2500 2400 2500
Text Notes 3900 2900 0    50   ~ 0
HW-357\n3.7V 9V 5V Adjustable PCB Step Up \n18650 Li-ion Battery Charge Discharge\nPower Bank Charger Module
Wire Wire Line
	6550 4400 7000 4400
Wire Wire Line
	5350 4400 6150 4400
Wire Wire Line
	9950 3200 9950 3500
Wire Wire Line
	6400 3300 6500 3300
Wire Wire Line
	6800 3300 7000 3300
Wire Wire Line
	6100 3300 6050 3300
Wire Wire Line
	6050 3300 6050 3450
Wire Wire Line
	9250 3500 9500 3500
Wire Wire Line
	9800 3500 9950 3500
Wire Wire Line
	9800 3200 9950 3200
Wire Wire Line
	9250 3200 9500 3200
Wire Wire Line
	8600 3500 8950 3500
Wire Wire Line
	9950 3800 9950 3500
Connection ~ 9950 3500
$Comp
L power:GND #PWR?
U 1 1 5EFF124B
P 6050 3450
F 0 "#PWR?" H 6050 3200 50  0001 C CNN
F 1 "GND" H 6055 3277 50  0000 C CNN
F 2 "" H 6050 3450 50  0001 C CNN
F 3 "" H 6050 3450 50  0001 C CNN
	1    6050 3450
	1    0    0    -1  
$EndComp
$EndSCHEMATC
