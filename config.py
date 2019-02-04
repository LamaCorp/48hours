import os
import re
import pygame
import configlib
from constants import LEVELS_GRAPHICAL_FOLDER, ASSETS

BLOCKS_BASE_REGEX = r'_[0-9]*\.png'
LAVA_REGEX = re.compile(r'lava_[0-9]*\.png')


def get_available(what, where):
    names = []

    for file in os.listdir(where):
        name = os.path.basename(file)
        match = what.match(name)
        if match:
            names.append(match.group(0).title())

    return sorted(names)


get_lava_sheets = get_available(LAVA_REGEX, os.path.join(LEVELS_GRAPHICAL_FOLDER, "lava"))


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
    '0': ("ez_pz.map", "0: EZ PZ"),
    '1': ("can_we_get_started.map", "1: Can we get started?"),
    '2': ("a_bit_more_boring_stuff.map", "2: A bit more boring stuff"),
    '3': ("round_and_round.map", "3: Round and round"),
    '4': ("here_we_go.map", "4: Here we go"),
    '5': ("insert_emotion.map", "5: Insert Emotion"),
    '6': ("garry.map", "6: Get your shit together, Garry"),
    '7': ("getting_to_know_each_other.map", "7: Getting to know each other"),
    '8': ("hf_bro.map", "8: HF bro"),
    '9': ("highway_to_hell.map", "9: Highway to Hell")
}

KEYS_DICTS = {
    "MOVE": {
        "WASD": (pygame.K_a, pygame.K_d),
        "ZQSD": (pygame.K_q, pygame.K_d),
        "Arrows": (pygame.K_LEFT, pygame.K_RIGHT),
    },
    "RUN": {
        "Left Shift": pygame.K_LSHIFT,
        "Right Shift": pygame.K_RSHIFT,
        "Left Ctrl": pygame.K_LCTRL,
        "Right Ctrl": pygame.K_RCTRL,
    },
    "JUMP": {
        "Space bar": pygame.K_SPACE,
        "W": pygame.K_w,
        "Z": pygame.K_z,
        "Up arrow": pygame.K_UP,
    },
}


class Config(configlib.Config):
    __config_path__ = os.path.abspath(os.path.join(ASSETS, "config.json"))

    level = 0

    player = 0

    key_bindings = {
        "LEFT": [pygame.K_LEFT],
        "RIGHT": [pygame.K_RIGHT],
        "JUMP": [pygame.K_SPACE],
        "RUN": [pygame.K_LSHIFT],
    }

    levels_stats = {
        '0': [0, -1, 0, 0, ],  # number of deaths in the level,
        '1': [0, -1, 0, 0, ],  # best time,
        '2': [0, -1, 0, 0, ],  # has the AK-47 been taken?,
        '3': [0, -1, 0, 0, ],  # number of blocks popped,
        '4': [0, -1, 0, 0, ],
        '5': [0, -1, 0, 0, ],
        '6': [0, -1, 0, 0, ],
        '7': [0, -1, 0, 0, ],
        '8': [0, -1, 0, 0, ],
        '9': [0, -1, 0, 0, ]
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
