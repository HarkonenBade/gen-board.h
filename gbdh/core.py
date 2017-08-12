#! /usr/bin/env python3

import argparse
import collections
import sys

import jinja2
import yaml

from .mcu import get_mcu


class Pins:
    _Pin = collections.namedtuple("Pin", ['name', 'port', 'num',
                                          'mode', 'od', 'otype',
                                          'ospeed', 'pupd', 'af',
                                          'raw'])

    modes = ('MODE', 'OTYPE', 'OSPEED', 'PUPD', 'OD')

    def __init__(self, board_def):
        self.mcu = get_mcu(board_def['mcutype'])

        default = self._load_default(board_def['default'])

        self._pins = {port: [self._Pin(name="PIN{}".format(n),
                                       port=port,
                                       num=n,
                                       **default)
                             for n in range(self.mcu.pins_per_port)]
                      for port in self.mcu.ports}

        self._pins_by_name = {}

        for name, pin_data in board_def['pins'].items():
            pin = self._parse_pin_data(name, pin_data, default)
            self._pins[pin.port][pin.num] = pin
            self._pins_by_name[pin.name] = pin

    def _parse_data_str(self, pin_data):
        def err(reason):
            print("Error: At definition '{}'".format(pin_data))
            print(reason)
            sys.exit(1)

        pin = {}
        raw = []
        for elm in pin_data.split(","):
            elm = elm.strip().upper()
            if(elm[0] == "P" and
               elm[1] in self.mcu.ports and
               int(elm[2:]) < self.mcu.pins_per_port):
                pin['port'] = elm[1]
                pin['num'] = int(elm[2:])
            elif elm in ['INPUT',
                         'OUTPUT',
                         'ANALOG']:
                if 'mode' in pin:
                    if pin['mode'] == "ALTERNATE":
                        err("You cannot specify both an AF and a mode")
                    else:
                        err("You cannot specify two modes for a pin")
                pin['mode'] = elm
                pin['af'] = 0
                raw += [elm]
            elif elm in ['STARTLOW',
                         'STARTHIGH']:
                if 'od' in pin:
                    err("You cannot specify two od values for a pin")
                pin['od'] = elm.replace("START", "")
                raw += [elm]
            elif elm in ['PUSHPULL',
                         'OPENDRAIN']:
                if 'otype' in pin:
                    err("You cannot specify two otype values for a pin")
                pin['otype'] = elm
                raw += [elm]
            elif elm in ['VERYLOWSPEED',
                         'LOWSPEED',
                         'MEDIUMSPEED',
                         'HIGHSPEED']:
                if 'ospeed' in pin:
                    err("You cannot specify two speed values for a pin")
                pin['ospeed'] = elm.replace("SPEED", "")
                raw += [elm]
            elif elm in ['FLOATING',
                         'PULLUP',
                         'PULLDOWN']:
                if 'pupd' in pin:
                    err("You cannot specify two pupd values for a pin")
                pin['pupd'] = elm
                raw += [elm]
            elif elm[:2] == "AF":
                if 'mode' in pin:
                    err("You cannot specify both an AF and a mode")
                pin['mode'] = "ALTERNATE"
                pin['af'] = int(elm[2:])
                raw += [elm]
            else:
                err("Invalid pin keyword '{}'".format(elm))
        pin['raw'] = " ".join(raw).lower()
        return pin

    def _load_default(self, default):
        pin = self._parse_data_str(default)
        pin['raw'] = "unused"
        if 'mode' not in pin:
            print("Error: Default must specify either INPUT, OUTPUT, ANALOG or an AF.")
            sys.exit(1)
        elif 'od' not in pin:
            print("Error: Default must specify either STARTLOW or STARTHIGH.")
            sys.exit(1)
        elif 'otype' not in pin:
            print("Error: Default must specify either PUSHPULL or OPENDRAIN.")
            sys.exit(1)
        elif 'ospeed' not in pin:
            print("Error: Default must specify either VERYLOWSPEED, LOWSPEED, MEDIUMSPEED, HIGHSPEED.")
            sys.exit(1)
        elif 'pupd' not in pin:
            print("Error: Default must specify either FLOATING, PULLUP or PULLDOWN.")
            sys.exit(1)
        elif 'port' in pin:
            print("Error: You cannot specify a PXN for default.")
            sys.exit(1)
        return pin

    def _parse_pin_data(self, name, pin_data, default):
        pin = {"name": name.upper()}
        pin.update(default)
        data = self._parse_data_str(pin_data)
        pin.update(data)
        return self._Pin(**pin)

    def names(self):
        for _, pin in sorted(self._pins_by_name.items()):
            yield pin

    def ports(self):
        return sorted(self._pins)

    def port(self, port):
        return self._pins[port.upper()]


def process_yaml(board_def):
    # Voltages in the form 330 (3v3), 500 (5v)
    board_def['voltage'] = int(board_def['voltage']*100)
    board_def['pins'] = Pins(board_def)
    return board_def


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("yamlfile",
                        type=argparse.FileType(),
                        help="YAML board definition fle to read.")
    parser.add_argument("outfile",
                        type=argparse.FileType('w'),
                        default="board.h",
                        nargs="?",
                        help="File to write to. [board.h]")

    return parser.parse_args()


def format_board_name(name):
    return ''.join([c.upper() if c.isalnum() else "_" for c in name])


def main():
    args = get_args()

    with args.yamlfile:
        board_def = yaml.safe_load(args.yamlfile)

    board_def = process_yaml(board_def)

    env = jinja2.Environment(loader=jinja2.PackageLoader('gbdh', ''),
                             trim_blocks=True,
                             lstrip_blocks=True)
    env.filters['format_board_name'] = format_board_name
    tmpl = env.get_template("board.tmpl")
    with args.outfile:
        tmpl.stream(yamlfile=args.yamlfile.name, **board_def).dump(args.outfile)
