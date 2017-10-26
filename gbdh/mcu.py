import collections
import sys


MCU = collections.namedtuple('MCU', ['ports', 'pins_per_port'])


MCU_LIST = {
    'STM32F0': MCU(ports=['A', 'B', 'C', 'D', 'F'],
                   pins_per_port=16),
    'STM32F4': MCU(ports=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],
                   pins_per_port=16),
    'STM32L0': MCU(ports=['A', 'B', 'C'],
                   pins_per_port=16)
}


def get_mcu(mcu_type):
    def match_names(test, x):
        if test.upper().startswith(x.upper()):
            return len(x)
        else:
            return -1

    rank_types = sorted(MCU_LIST.keys(),
                        key=lambda x: match_names(mcu_type, x),
                        reverse=True)
    choice = rank_types[0]
    score = match_names(mcu_type, choice)

    if score <= 0:
        print("Error: No matching mcu type definition found.")
        sys.exit(1)

    return MCU_LIST[choice]
