import os
import re
import configlib
from constants import LEVELS_GRAPHICAL_FOLDER, ASSETS

BLOCKS_BASE_REGEX = r'_[0-9]*\.png'


def get_available(what, where):
    names = []

    for file in os.listdir(where):
        name = os.path.basename(file)
        match = what.match(name)
        if match:
            names.append(match.group(0).title())

    return sorted(names)


def get_available_blocks(block_type="dirt"):
    block_regex = re.compile(block_type + BLOCKS_BASE_REGEX)
    return get_available(block_regex, LEVELS_GRAPHICAL_FOLDER)


PLAYERS = {
    0: ("lama_normal.png", "Lama"),
    1: ("lama_shadow.png", "Shadow"),
    2: ("lama_licorne.png", "Unicorn"),
    3: ("lama_rasta.png", "Rasta"),
    4: ("lama_kilt.png", "Irish"),
    5: ("lama_gay.png", "Gaaaaaay"),
    6: ("lama_gay_kilt.png", "Gay Irish"),
}

LEVELS = {
    0: ("level_0.map", "0: EZ PZ"),
    1: ("level_1.map", "1: Can we get started?"),
    2: ("level_2.map", "2: Get your shit together, Garry"),
    3: ("level_3.map", "3: Getting to know each other"),
}

get_available_levels = [LEVELS[l][1] for l in LEVELS]
get_available_players = [PLAYERS[p][1] for p in PLAYERS]


def get_index_from_name(DIC, name):
    for i in DIC:
        if DIC[i][1] == name:
            return i
    return -1


class Config(configlib.Config):
    __config_path__ = os.path.abspath(os.path.join(ASSETS, "config.json"))

    level = 0

    player = 0


CONFIG = Config()

if __name__ == '__main__':
    configlib.update_config(Config)
