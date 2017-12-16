# gen-board.h

Python script for generating ChibiOS board.h files based on a consise yaml representation.

See board.yaml.example for examples of the yaml syntax.

## Required Parameters
All boards require the below parameters:

KEY|DESCRIPTION
---|-----------
NAME|Name of the board
LSEFREQ|LSE Frequency
HSEFREQ|HSE Frequency
VOLTAGE|Voltage as decimal (eg *3.3*)
MCUTYPE|Type of MCU (eg *STM32F405xx*)
DEFAULT|List of default attributes for pins
PINS|Pin names and corresponding lists of attributes

## Other Parameters
Board-specific parameters can be included under the 'other' key, such as *STM32_LSEDRV* and *STM32_HSE_BYPASS*.

If the parameter does not have a value associated with it, use *null* or *~*.

## Attributes
Pins may be given a variety of attributes that come from several categories, multiple attributes from the same category is not supported.

MODE|OTYPE|OSPEED|PUPD|OD
----|-----|------|----|--
INPUT|PUSHPULL|VERYLOWSPEED|FLOATING|STARTLOW
OUTPUT|OPENDRAIN|LOWSPEED|PULLUP|STARTHIGH
ANALOG||MEDIUMSPEED|PULLDOWN|
AF1,AF2,AF3...||HIGHSPEED||
