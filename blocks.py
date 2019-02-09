import os
import re
import random
import time
from functools import partial, lru_cache
import pygame
import logging

from constants import DEFAULT_BLOCK_SIZE, LEVELS_GRAPHICAL_FOLDER, ASSETS
from config import get_lava_sheets
from entities import Brochette
from helper import classproperty
from physics import Pos

LOGGER = logging.getLogger(__name__)


@lru_cache()
def get_boom_img(i):
    path = os.path.join(LEVELS_GRAPHICAL_FOLDER, 'boom', f'BOOOM{i}.png')
    img = pygame.image.load(path).convert()
    img.set_colorkey((0, 0, 0))
    return img


def re_compile(matrix):
    """Compile the matrix of pattern and replace the " " by dots to match the air."""
    not_solid = "".join([b().character for b in BLOCKS if not b().solid]) + Block.character + EndBlock.character
    solid = "".join([b().character for b in BLOCKS if b().solid and b is not EndBlock])
    not_solid = f"[{re.escape(not_solid)}]"
    solid = f"[{re.escape(solid)}]"

    compiled = []
    for line in matrix:
        compiled_line = []
        for pattern in line:
            pattern = pattern.replace(" ", not_solid)
            pattern = pattern.replace("?", solid)
            pattern = re.compile(pattern)
            compiled_line.append(pattern)
        compiled.append(compiled_line)
    return compiled


class Block:
    DEFAULT_BLOCK_SIZE = DEFAULT_BLOCK_SIZE
    IGNORE_IMG_CACHE = False

    character = '.'
    _sheet = None
    sheet = None  # type: pygame.Surface
    default_sprite_pos = (0, 0)
    solid = False
    visible = False
    deadly = False
    rotation = 0
    sheet_pattern = [[]]

    def __init__(self, pos=(0, 0)):
        self.pos = pos
        self.exploded = False
        self.explode_frame = 1

    @staticmethod
    def new(character='.', pos=(0, 0)):
        dic = {
            "D": Dirt,
            "S": Stone,
            "H": Bush,
            "F": Cloud,
            "C": CatCloud,
            "L": Lava,
            "B": Barbecue,
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

    def explode(self):
        self.exploded = True

    @classmethod
    # @lru_cache()
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

    @classproperty
    @lru_cache()
    def sheet_pattern(cls):
        # . is any block
        # ? is any solid
        # " " is any non solid block
        return re_compile([
            [". . ??.?.", ". .??????", ". .?? .?.", ". . ? .?.", "???????? ", "?????? ??"],
            [".?. ??.?.", "?????????", ".?.?? .?.", ".?. ? .?.", ".? .?????", " ?.??.???"],
            [".?? ??. .", ".?.???. .", "??.?? . .", ".?. ? . .", ". . ??.? ", ". .??  ?."],
            [". . ??. .", ". .???. .", ". .?? . .", ". . ? . .", ".?  ??. .", " ?.?? . ."],
            [". .??? ??", ". .??? ? ", ". .????? ", ".?. ?? ? ", ".?.??  ? "]
        ])

    @classproperty
    def sheet(cls):
        if cls._sheet is None:
            LOGGER.info("Dirt - Setting sheet")
            sheet = pygame.image.load(os.path.join(LEVELS_GRAPHICAL_FOLDER, "dirt_sheet.png")).convert()
            sheet.set_colorkey((255, 0, 255))
            sheet = pygame.transform.scale(sheet, (Pos(sheet.get_size()) * DEFAULT_BLOCK_SIZE / 16).i)
            cls._sheet = sheet
        return cls._sheet


class Stone(Block):
    character = "S"
    solid = True
    visible = True
    deadly = False
    default_sprite_pos = 1, 1

    @classproperty
    def sheet(cls):
        if cls._sheet is None:
            LOGGER.info("Stone - Setting sheet")
            sheet = pygame.image.load(os.path.join(LEVELS_GRAPHICAL_FOLDER, "stone_sheet.png")).convert()
            sheet.set_colorkey((255, 0, 255))
            sheet = pygame.transform.scale(sheet, (Pos(sheet.get_size()) * DEFAULT_BLOCK_SIZE / 16).i)
            cls._sheet = sheet
        return cls._sheet

    @classproperty
    @lru_cache()
    def sheet_pattern(cls):
        return re_compile([
            [". . ??.?.", ". .??????", ". .?? .?.", ". . ? .?."],  # "???.??.? ", "?????. ?."],
            [".?. ??.?.", "?????????", ".?.?? .?.", ".?. ? .?."],  # ".? .?????", " ?.??.???"],
            [".?. ??. .", ".?.???. .", ".?.?? . .", ".?. ? . ."],  # ". . ??.? ", ". .??  ?."],
            [". . ??. .", ". .???. .", ". .?? . .", ". . ? . ."],  # ".?  ??. .", " ?.?? . ."]
        ])


class Bush(Block):
    character = "H"
    solid = False
    visible = True
    deadly = False

    @classproperty
    def sheet(cls):
        if cls._sheet is None:
            LOGGER.info("Bush - Setting sheet")
            sheet = pygame.image.load(os.path.join(LEVELS_GRAPHICAL_FOLDER, "bush.png")).convert()
            sheet.set_colorkey((255, 0, 255))
            sheet = pygame.transform.scale(sheet, (DEFAULT_BLOCK_SIZE, DEFAULT_BLOCK_SIZE))
            cls._sheet = sheet
        return cls._sheet


class Cloud(Block):
    character = "F"
    solid = False
    visible = True
    deadly = False

    @classproperty
    def sheet(cls):
        if cls._sheet is None:
            LOGGER.info("Cloud - Setting sheet")
            sheet = pygame.image.load(os.path.join(LEVELS_GRAPHICAL_FOLDER, "cloud.png")).convert()
            sheet.set_colorkey((255, 0, 255))
            sheet = pygame.transform.scale(sheet, (DEFAULT_BLOCK_SIZE, DEFAULT_BLOCK_SIZE))
            cls._sheet = sheet
        return cls._sheet


class CatCloud(Block):
    character = "C"
    solid = False
    visible = True
    deadly = False

    @classproperty
    def sheet(cls):
        if cls._sheet is None:
            LOGGER.info("CatCloud - Setting sheet")
            sheet = pygame.image.load(os.path.join(LEVELS_GRAPHICAL_FOLDER, "cat_cloud.png")).convert()
            sheet.set_colorkey((255, 0, 255))
            sheet = pygame.transform.scale(sheet, (DEFAULT_BLOCK_SIZE, DEFAULT_BLOCK_SIZE))
            cls._sheet = sheet
        return cls._sheet


class Lava(Block):
    character = "L"
    solid = True
    visible = True
    deadly = True
    current_index = 0
    IGNORE_IMG_CACHE = True

    @classproperty
    def sheet(cls):
        if cls._sheet is None:
            sheets = [pygame.image.load(os.path.join(os.path.join(LEVELS_GRAPHICAL_FOLDER, "lava"),
                                                     path.lower())).convert()
                      for path in get_lava_sheets]
            sheets.reverse()
            for i in range(len(sheets)):
                sheets[i] = pygame.transform.scale(sheets[i], (DEFAULT_BLOCK_SIZE, DEFAULT_BLOCK_SIZE))
            cls._sheet = sheets
        cls.current_index = (time.time() * 15) % len(cls._sheet)
        return cls._sheet[int(cls.current_index)]


class Barbecue(Block):
    character = "B"
    solid = True
    visible = True
    deadly = True

    @classproperty
    def sheet(cls):
        if cls._sheet is None:
            LOGGER.info("Barbecue - Setting sheet")
            sheet = pygame.image.load(os.path.join(LEVELS_GRAPHICAL_FOLDER, "barbecue.png")).convert()
            sheet.set_colorkey((255, 0, 255))
            sheet = pygame.transform.scale(sheet, (DEFAULT_BLOCK_SIZE, DEFAULT_BLOCK_SIZE))
            cls._sheet = sheet
        return cls._sheet


class FieryBarbecue(Block):
    character = "^"
    solid = False
    visible = True
    deadly = True

    char_dic = {
        "^": (0, Pos(0, -1)),  # Rotation and direction of brochettes
        "V": (180, Pos(0, 1)),
        "<": (90, Pos(-1, 0)),
        ">": (-90, Pos(1, 0))
    }

    @classproperty
    def sheet(cls):
        if cls._sheet is None:
            LOGGER.info("FieryBarbecue - Setting sheet")
            sheet = pygame.image.load(os.path.join(LEVELS_GRAPHICAL_FOLDER, "fiery_barbecue.png")).convert()
            sheet.set_colorkey((255, 0, 255))
            sheet = pygame.transform.scale(sheet, (DEFAULT_BLOCK_SIZE, DEFAULT_BLOCK_SIZE))
            cls._sheet = sheet
        return cls._sheet

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

    @classproperty
    def sheet(cls):
        if cls._sheet is None:
            LOGGER.info("EndBlock - Setting sheet")
            sheet = pygame.image.load(os.path.join(ASSETS, "logo.png")).convert()
            sheet.set_colorkey((255, 0, 255))
            sheet = pygame.transform.scale(sheet, (DEFAULT_BLOCK_SIZE, DEFAULT_BLOCK_SIZE))
            cls._sheet = sheet
        return cls._sheet

    # This isn't called every frame. Instead, it is called when the player touches it
    def on_collision(self, level):
        level.explode()


BLOCKS = [
    Dirt,
    Stone,
    Cloud,
    CatCloud,
    Bush,
    Lava,
    Barbecue,
    FieryBarbecue,
    partial(FieryBarbecue, ">"),
    partial(FieryBarbecue, "<"),
    partial(FieryBarbecue, "V"),
    EndBlock,
]
