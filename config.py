import os
import re
import pygame
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
    4: ("lama_kilt.png", "Scottish"),
    5: ("lama_gay.png", "Gaaaaaay"),
    6: ("lama_gay_kilt.png", "Gay Scottish"),
}

LEVELS = {
    '0': ("level_0.map", "0: EZ PZ"),
    '1': ("level_1.map", "1: Can we get started?"),
    '2': ("level_2.map", "2: A bit more bring stuff"),
    '3': ("level_3.map", "3: Here we go"),
    '4': ("level_4.map", "4: Get your shit together, Garry"),
    '5': ("level_5.map", "5: Getting to know each other"),
}


class Config(configlib.Config):
    __config_path__ = os.path.abspath(os.path.join(ASSETS, "config.json"))

    level = 0

    player = 0

    key_bindings = {
        "LEFT": pygame.K_LEFT,
        "RIGHT": pygame.K_RIGHT,
        "JUMP": pygame.K_SPACE,
        "RUN": pygame.K_LSHIFT,
    }

    levels_stats = {
        '0': [0, -1, 0],  # Number of deaths in the level, best time, has the AK-47 been taken?
        '1': [0, -1, 0],
        '2': [0, -1, 0],
        '3': [0, -1, 0],
        '4': [0, -1, 0],
        '5': [0, -1, 0],
    }


CONFIG = Config()


get_available_levels = [LEVELS[l][1] for l in LEVELS]


def get_nb_ak47():
    total = 0
    for level in CONFIG.levels_stats:
        total += CONFIG.levels_stats[level][2]
    return total


def __get_available_players():
    nb_ak47 = get_nb_ak47()
    players_available = []
    for p in PLAYERS:
        if nb_ak47 >= p:
            players_available.append(PLAYERS[p][1])
    return players_available


get_available_players = __get_available_players()


def get_index_from_name(DIC, name):
    for i in DIC:
        if DIC[i][1] == name:
            return i
    return -1


if __name__ == '__main__':
    configlib.update_config(Config)
