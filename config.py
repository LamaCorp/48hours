import os
import re

from constants import PLAYER_FOLDER, MAPS_FOLDER, LEVELS_GRAPHICAL_FOLDER

LEVELS_REGEX = re.compile(r'level_[0-9]*\.map')
BLOCKS_BASE_REGEX = r'_[0-9]*\.png'
PLAYERS_REGEX = re.compile(r'lama_(.*)\.png')


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


get_available_players = get_available(PLAYERS_REGEX, PLAYER_FOLDER)


LEVELS = {
    0: ("level_0.map", "EZ PZ"),
    1: ("level_1.map", "Can we get started?"),
}


def get_level_index_from_name(name):
    for l in LEVELS:
        if LEVELS[l][1] == name:
            return l
    return -1


class LevelConfig:
    chosen_level = 0


class PlayerConfig:
    player = "lama_normal.png"
