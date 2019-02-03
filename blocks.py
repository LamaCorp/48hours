import os
import re
import random
from functools import partial, lru_cache

import pygame

from constants import DEFAULT_BLOCK_SIZE, LEVELS_GRAPHICAL_FOLDER, ASSETS
from entities import Brochette
from physics import Pos


def re_compile(matrix):
    """Compile the matrix of pattern and replace the " " by dots to match the air."""
    compiled = []
    for line in matrix:
        compiled_line = []
        for pattern in line:
            pattern = pattern.replace(" ", r"\.")
            pattern = pattern.replace("?", r"[DS]")
            pattern = re.compile(pattern)
            compiled_line.append(pattern)
        compiled.append(compiled_line)
    return compiled


class Block:
    DEFAULT_BLOCK_SIZE = DEFAULT_BLOCK_SIZE

    character = '.'
    sheet = None  # type: pygame.Surface
    default_sprite_pos = (0, 0)
    solid = False
    visible = False
    deadly = False
    rotation = 0
    sheet_pattern = [[]]

    def __init__(self, pos=(0, 0)):
        self.pos = pos

    @staticmethod
    def new(character='.', pos=(0, 0)):
        dic = {
            "D": Dirt,
            "S": Stone,
            "B": Barbecue,
            "K": AK47,
            "E": EndBlock,
            "V": partial(FieryBarbecue, "V"),
            "^": partial(FieryBarbecue, "^"),
            "<": partial(FieryBarbecue, "<"),
            ">": partial(FieryBarbecue, ">")
        }

        return dic.get(character, Block)(pos)

    def get_img(self, neighbourg="", rotation=0):
        """Neighbourg is a string of nine chars of the 9 blocks next to this one."""

        for y, line in enumerate(self.sheet_pattern):
            for x, pattern in enumerate(line):
                if pattern.match(neighbourg):
                    return self.img_at(x, y, rotation)

        return self.img_at(*self.default_sprite_pos, rotation=rotation)

    @classmethod
    @lru_cache()
    def img_at(cls, x, y, rotation=0):
        return pygame.transform.rotate(cls.sheet.subsurface((x * cls.DEFAULT_BLOCK_SIZE, y * cls.DEFAULT_BLOCK_SIZE,
                                                             cls.DEFAULT_BLOCK_SIZE, cls.DEFAULT_BLOCK_SIZE)), rotation)

    def internal_logic(self, level):
        pass

    def on_collision(self, level):
        pass


class Dirt(Block):
    character = "D"
    solid = True
    visible = True
    deadly = False
    default_sprite_pos = 1, 1
    sheet = pygame.image.load(os.path.join(LEVELS_GRAPHICAL_FOLDER, "dirt_sheet.png")).convert()
    sheet.set_colorkey((255, 0, 255))
    sheet = pygame.transform.scale(sheet, (Pos(sheet.get_size()) * DEFAULT_BLOCK_SIZE / 16).i)

    # . is any block
    # ? is any block but not air
    # " " is only air
    sheet_pattern = re_compile([
        [". . ??.?.", ". .??????", ". .?? .?.", ". . ? .?.", "???.??.? ", "?????. ?."],
        [".?. ??.?.", "?????????", ".?.?? .?.", ".?. ? .?.", ".? .?????", " ?.??.???"],
        [".?. ??. .", ".?.???. .", ".?.?? . .", ".?. ? . .", ". . ??.? ", ". .??  ?."],
        [". . ??. .", ". .???. .", ". .?? . .", ". . ? . .", ".?  ??. .", " ?.?? . ."]
    ])


class Stone(Block):
    character = "S"
    solid = True
    visible = True
    deadly = False
    default_sprite_pos = 1, 1

    sheet = pygame.image.load(os.path.join(LEVELS_GRAPHICAL_FOLDER, "stone_sheet.png")).convert()
    sheet.set_colorkey((255, 0, 255))
    sheet = pygame.transform.scale(sheet, (Pos(sheet.get_size()) * DEFAULT_BLOCK_SIZE / 16).i)

    sheet_pattern = re_compile([
        [". . ??.?.", ". .??????", ". .?? .?.", ". . ? .?."],  # "???.??.? ", "?????. ?."],
        [".?. ??.?.", "?????????", ".?.?? .?.", ".?. ? .?."],  # ".? .?????", " ?.??.???"],
        [".?. ??. .", ".?.???. .", ".?.?? . .", ".?. ? . ."],  # ". . ??.? ", ". .??  ?."],
        [". . ??. .", ". .???. .", ". .?? . .", ". . ? . ."],  # ".?  ??. .", " ?.?? . ."]
    ])


class Barbecue(Block):
    character = "B"
    solid = True
    visible = True
    deadly = True

    sheet = pygame.image.load(os.path.join(LEVELS_GRAPHICAL_FOLDER, "barbecue.png")).convert()
    sheet.set_colorkey((255, 0, 255))
    sheet = pygame.transform.scale(sheet, (DEFAULT_BLOCK_SIZE, DEFAULT_BLOCK_SIZE))


class FieryBarbecue(Block):
    character = "^"
    solid = False
    visible = True
    deadly = True

    sheet = pygame.image.load(os.path.join(LEVELS_GRAPHICAL_FOLDER, "fiery_barbecue.png")).convert()
    sheet.set_colorkey((255, 0, 255))
    sheet = pygame.transform.scale(sheet, (DEFAULT_BLOCK_SIZE, DEFAULT_BLOCK_SIZE))

    char_dic = {
        "^": (0, Pos(0, -1)),  # Rotation and direction of brochettes
        "V": (180, Pos(0, 1)),
        "<": (90, Pos(-1, 0)),
        ">": (-90, Pos(1, 0))
    }

    def __init__(self, character="^", pos=(0, 0)):
        super().__init__(pos)
        self.character = character
        self.rotation = FieryBarbecue.char_dic[self.character][0]
        self.next_spawn = random.randint(5, 30)
        self.brochettes = []

    def internal_logic(self, level):
        self.next_spawn -= 1
        if self.next_spawn <= 0:
            level.spawn(Brochette(level.map_to_world(self.pos), FieryBarbecue.char_dic[self.character]))
            self.next_spawn = random.randint(60, 90)


class EndBlock(Block):
    character = "E"
    solid = True
    visible = True
    deadly = False

    sheet = pygame.image.load(os.path.join(ASSETS, "logo.png")).convert()
    sheet.set_colorkey((255, 0, 255))
    sheet = pygame.transform.scale(sheet, (DEFAULT_BLOCK_SIZE, DEFAULT_BLOCK_SIZE))

    # This isn't called every frame. Instead, it is called when the player touches it
    def on_collision(self, level):
        level.explode()


class AK47(Block):
    character = "K"
    solid = False
    visible = True
    deadly = False

    sheet = pygame.image.load(os.path.join(LEVELS_GRAPHICAL_FOLDER, "ak47.png")).convert()
    sheet.set_colorkey((255, 0, 255))
    sheet = pygame.transform.scale(sheet, (DEFAULT_BLOCK_SIZE, DEFAULT_BLOCK_SIZE))
