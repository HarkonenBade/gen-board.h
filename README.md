# gen-board.h

Python script for generating ChibiOS board.h files based on a consise yaml representation.

## Attributes
Pins may be given a variety of attributes that come from several categories, multiple attributes from the same category is not supported.

MODE|OTYPE|OSPEED|PUPD|OD
----|-----|------|----|--
INPUT|PUSHPULL|VERYLOWSPEED|FLOATING|STARTLOW
OUTPUT|OPENDRAIN|LOWSPEED|PULLUP|STARTHIGH
ANALOG||MEDIUMSPEED|PULLDOWN|
AF1,AF2,AF3...||HIGHSPEED||

See board.yaml.example for examples of the yaml syntax.
