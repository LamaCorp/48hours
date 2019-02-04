import os
from functools import lru_cache

import pygame

from constants import KEYS_FOLDER

index_to_name = list("abcdefghijklmnopqrstuvwxyz0123456789")
index_to_name.extend([
    "right",
    "left",
    "up",
    "down",
])
index_to_name.extend(".,;:'\"<>/\\|()[]{}+-*=_~!?#")
index_to_name.extend([
    "left shift",
    "right shift",
    "right ctrl",
    "left ctrl",
    "caps lock",
    "return",
    "space",
])

@lru_cache()
def name_to_img(name):
    if name in index_to_name:
        name = f'keys_{index_to_name.index(name)}.png'
    else:
        # the last img (and it's NOT in index_to_name) is a \_O.o_/
        print(f"Missing key {name}")
        name = f'keys_{len(index_to_name)}.png'

    img = pygame.image.load(os.path.join(KEYS_FOLDER, name)).convert()
    img.set_colorkey((255, 0, 255))
    return img





