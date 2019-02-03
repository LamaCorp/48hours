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

    print(names)
    return sorted(names)


def get_available_blocks(block_type="dirt"):
    block_regex = re.compile(block_type + BLOCKS_BASE_REGEX)
    return get_available(block_regex, LEVELS_GRAPHICAL_FOLDER)


get_available_levels = get_available(LEVELS_REGEX, MAPS_FOLDER)
get_available_players = get_available(PLAYERS_REGEX, PLAYER_FOLDER)


class LevelConfig:
    chosen_level = "Level_0.Map"


class PlayerConfig:
    player = "lama_normal.png"
