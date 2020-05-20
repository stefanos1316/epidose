EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title "Epidose: Raspberry Pi contact tracing"
Date "2020-05-20"
Rev "1.0"
Comp "Author: Diomidis Spinellis"
Comment1 "License: CC-BY"
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L LED:IR204A D1
U 1 1 5EC54C71
P 3500 1750
F 0 "D1" H 3450 2040 50  0000 C CNN
F 1 "Mini LED; red" H 3450 1949 50  0000 C CNN
F 2 "LED_THT:LED_D3.0mm_IRBlack" H 3500 1925 50  0001 C CNN
F 3 "" H 3450 1750 50  0001 C CNN
	1    3500 1750
	1    0    0    -1  
$EndComp
$Comp
L Switch:SW_SPST SW1
U 1 1 5EC5601D
P 3400 2250
F 0 "SW1" H 3400 2485 50  0000 C CNN
F 1 "SW_SPST momentary press" H 3400 2394 50  0000 C CNN
F 2 "" H 3400 2250 50  0001 C CNN
F 3 "~" H 3400 2250 50  0001 C CNN
	1    3400 2250
	1    0    0    -1  
$EndComp
$Comp
L Device:R R1
U 1 1 5EC5713D
P 2900 1750
F 0 "R1" V 2693 1750 50  0000 C CNN
F 1 "330Ω" V 2784 1750 50  0000 C CNN
F 2 "" V 2830 1750 50  0001 C CNN
F 3 "~" H 2900 1750 50  0001 C CNN
	1    2900 1750
	0    1    1    0   
$EndComp
Wire Wire Line
	3050 1750 3300 1750
Text GLabel 4150 1750 2    50   Input ~ 0
BCM21
Wire Wire Line
	3600 1750 4150 1750
Text GLabel 4150 2250 2    50   Input ~ 0
BCM15
Wire Wire Line
	3600 2250 4150 2250
$Comp
L power:GND #PWR1
U 1 1 5EC58E9E
P 2600 1750
F 0 "#PWR1" H 2600 1500 50  0001 C CNN
F 1 "GND" H 2605 1577 50  0000 C CNN
F 2 "" H 2600 1750 50  0001 C CNN
F 3 "" H 2600 1750 50  0001 C CNN
	1    2600 1750
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5EC59D6F
P 2600 2250
F 0 "#PWR?" H 2600 2000 50  0001 C CNN
F 1 "GND" H 2605 2077 50  0000 C CNN
F 2 "" H 2600 2250 50  0001 C CNN
F 3 "" H 2600 2250 50  0001 C CNN
	1    2600 2250
	1    0    0    -1  
$EndComp
Wire Wire Line
	2750 1750 2600 1750
Wire Wire Line
	3200 2250 2600 2250
Text Notes 4200 1700 0    50   ~ 0
Pin 40
Text Notes 4200 2200 0    50   ~ 0
Pin 10
Text Notes 2500 2200 0    50   ~ 0
Pin 14
Text Notes 2500 1700 0    50   ~ 0
Pin 20
$EndSCHEMATC
