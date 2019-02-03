import os
import re
from functools import lru_cache, partial
from typing import List

import pygame

from constants import LEVELS_GRAPHICAL_FOLDER, MAPS_FOLDER, DEFAULT_BLOCK_SIZE
from entities import Brochette
from physics import Space, Pos, clamp

START = "P"


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
        [". . ??.?.", ". .??????", ". .?? .?.", ". . ? .?."], #"???.??.? ", "?????. ?."],
        [".?. ??.?.", "?????????", ".?.?? .?.", ".?. ? .?."], #".? .?????", " ?.??.???"],
        [".?. ??. .", ".?.???. .", ".?.?? . .", ".?. ? . ."], #". . ??.? ", ". .??  ?."],
        [". . ??. .", ". .???. .", ". .?? . .", ". . ? . ."], #".?  ??. .", " ?.?? . ."]
    ])


class Barbecue(Block):
    character = "B"
    solid = False
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
        self.next_spawn = 5
        self.brochettes = []

    def internal_logic(self, level):
        self.next_spawn -= 1
        if self.next_spawn == 0:
            level.spawn(Brochette(level.map_to_world(self.pos), FieryBarbecue.char_dic[self.character][1]))
            self.next_spawn = 45


class Level:
    OFFSET_THRESHOLD = 40 / 100

    def __init__(self, level='level_0'):
        self.name = level
        self.space = Space(self, gravity=(0, 1))
        self.size = Pos(0, 0)
        self.grid = []  # type: List[List[Block]]
        self.start = (0, 0)  # Where the players has to spawn, map coordinates
        self.offset = Pos(0, 0)  # Where we start to draw the map, world coordinates
        self.load_level()
        self.screen_size = (0, 0)

    @property
    def world_start(self):
        return self.map_to_world(self.start)

    @staticmethod
    def map_to_world(map_pos):
        return Pos(map_pos[0] * Block.DEFAULT_BLOCK_SIZE, map_pos[1] * Block.DEFAULT_BLOCK_SIZE)

    @staticmethod
    def world_to_map(world_pos):
        return (Pos(world_pos) // Block.DEFAULT_BLOCK_SIZE).i

    def get_block(self, map_pos):
        x, y = map_pos
        if (0 <= x < self.size.x
                and 0 <= y < self.size.y):
            return self.grid[y][x]

        return Stone()

    def get_slice(self, map_top_left, map_bottom_right):
        """Return a list of all block totally covering the given rectangle."""
        for y in range(map_top_left[1], map_bottom_right[1] + 1):
            for x in range(map_top_left[0], map_bottom_right[0] + 1):
                yield self.get_block((x, y))

    def get_block_world_rect(self, map_pos):
        """Get the rect for collision checking of the block at the given position"""
        return (
            self.map_to_world(map_pos),
            (Block.DEFAULT_BLOCK_SIZE, Block.DEFAULT_BLOCK_SIZE)
        )

    def get_block_at_world(self, world_pos):
        map_pos = self.world_to_map(world_pos)
        return self.get_block(map_pos)

    @lru_cache(maxsize=None)
    def get_img_at(self, map_pos):
        neigh = "".join(self.get_block((map_pos[0] + dx, map_pos[1] + dy)).character
                        for dy in range(-1, 2)
                        for dx in range(-1, 2))
        block = self.get_block(map_pos)
        return block.get_img(neigh, rotation=block.rotation)

    @property
    def world_size(self):
        """(width, height), in pixels"""
        return Level.map_to_world(self.size)

    def load_level(self):  # TODO: may we improve this?
        with open(os.path.join(MAPS_FOLDER, self.name.lower()), 'r') as map_file:
            height, width = list(map(int, map_file.readline().split()))
            self.size = Pos(width, height)
            for h in range(height):
                line = list(map_file.readline().strip())
                for i in range(len(line)):
                    if line[i] == START:
                        self.start = (i, h)
                    line[i] = Block.new(line[i], (i, h))
                self.grid.append(line)

    def update_offset(self, player_pos, screen_size):
        player_pos = player_pos - self.offset
        if player_pos[0] < self.OFFSET_THRESHOLD * screen_size[0]:
            self.offset = (self.offset[0] - (self.OFFSET_THRESHOLD * screen_size[0] - player_pos[0]),
                           self.offset[1])
        elif player_pos[0] > (1 - self.OFFSET_THRESHOLD) * screen_size[0]:
            self.offset = (self.offset[0] + (player_pos[0] - (1 - self.OFFSET_THRESHOLD) * screen_size[0]),
                           self.offset[1])
        if player_pos[1] < self.OFFSET_THRESHOLD * screen_size[1]:
            self.offset = (self.offset[0],
                           self.offset[1] - (self.OFFSET_THRESHOLD * screen_size[1] - player_pos[1]))
        elif player_pos[1] > (1 - self.OFFSET_THRESHOLD) * screen_size[1]:
            self.offset = (self.offset[0],
                           self.offset[1] + (player_pos[1] - (1 - self.OFFSET_THRESHOLD) * screen_size[1]))

        self.offset = Pos(clamp(self.offset[0],
                                Block.DEFAULT_BLOCK_SIZE,
                                self.world_size.x - screen_size[0] - Block.DEFAULT_BLOCK_SIZE),
                          clamp(self.offset[1],
                                Block.DEFAULT_BLOCK_SIZE,
                                self.world_size.y - screen_size[1] - Block.DEFAULT_BLOCK_SIZE))

    def internal_logic(self):
        offset_end = (self.offset + self.screen_size).t
        for line in range(clamp(Level.world_to_map(self.offset)[1] - 20, 0, self.size[1] - 1),
                          clamp(Level.world_to_map(offset_end)[1] + 20, 0, self.size[1] - 1)):
            for block in range(clamp(Level.world_to_map(self.offset)[0] - 20, 0, self.size[0] - 1),
                               clamp(Level.world_to_map(offset_end)[0] + 20, 0, self.size[0] - 1)):
                block = self.grid[line][block]
                block.internal_logic(self)

    def render(self, surf):
        self.screen_size = Pos(surf.get_size())
        offset_end = (self.offset + self.screen_size).t
        for line in range(Level.world_to_map(self.offset)[1],
                          clamp(Level.world_to_map(offset_end)[1] + 2, 0, self.size[1] - 1)):
            for block in range(Level.world_to_map(self.offset)[0],
                               clamp(Level.world_to_map(offset_end)[0] + 2, 0, self.size[0] - 1)):
                if self.grid[line][block].visible:
                    surf.blit(self.get_img_at((block, line)), self.map_to_world((block, line)) - self.offset)

        for body in self.space.moving_bodies:
            body.render(surf, -self.offset)

    def spawn(self, body):
        self.space.add(body)
