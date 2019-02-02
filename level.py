import os
import re
from functools import lru_cache
from typing import List

import pygame

from constants import LEVELS_GRAPHICAL_FOLDER, MAPS_FOLDER, DEFAULT_BLOCK_SIZE
from physics import Space, Pos, clamp

START = "P"


def re_compile(matrix):
    """Compile the matrix of pattern and replace the " " by dots to match the air."""
    compiled = []
    for line in matrix:
        compiled_line = []
        for pattern in line:
            pattern = pattern.replace(" ", r"\.")
            pattern =  pattern.replace("?", r"[DS]")
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
    sheet_pattern = [[]]

    @staticmethod
    def new(character='.'):
        dic = {
            "D": Dirt,
            "S": Stone,
            "B": Barbecue,
        }

        return dic.get(character, Block)()

    def get_img(self, neighbourg=""):
        """Neighbourg is a string of nine chars of the 9 blocks next to this one."""

        for y, line in enumerate(self.sheet_pattern):
            for x, pattern in enumerate(line):
                if pattern.match(neighbourg):
                    return self.img_at(x, y)

        return self.img_at(*self.default_sprite_pos)

    @classmethod
    @lru_cache()
    def img_at(cls, x, y):
        return cls.sheet.subsurface((x * cls.DEFAULT_BLOCK_SIZE, y * cls.DEFAULT_BLOCK_SIZE,
                                     cls.DEFAULT_BLOCK_SIZE, cls.DEFAULT_BLOCK_SIZE))

    def render(self, surf, pos=None, neighbours=""):
        if self.solid:
            surf.blit(self.get_img(neighbours), pos)


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
    solid = True
    visible = True
    deadly = True

    sheet = pygame.image.load(os.path.join(LEVELS_GRAPHICAL_FOLDER, "barbecue.png")).convert()
    sheet.set_colorkey((255, 0, 255))
    sheet = pygame.transform.scale(sheet, (DEFAULT_BLOCK_SIZE, DEFAULT_BLOCK_SIZE))


class Level:
    OFFSET_THRESHOLD = 40 / 100

    def __init__(self, level='level_0'):
        self.name = level
        self.space = Space(self, gravity=(0, 1))
        self.size = Pos(0, 0)
        self.grid = []  # type: List[List[Block]]
        self.start = (0, 0)  # Where the player has to spawn, map coordinates
        self.offset = Pos(0, 0)  # Where we start to draw the map, world coordinates
        self.load_level()

    @property
    def world_start(self):
        return self.map_to_world(self.start)

    @staticmethod
    def map_to_world(map_pos):
        return Pos(map_pos) * Block.DEFAULT_BLOCK_SIZE

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
        return block.get_img(neigh)

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
                    line[i] = Block.new(line[i])
                self.grid.append(line)

    def update_offset(self, player_pos, screen_size):
        player_pos = Pos(player_pos) - Pos(self.offset)
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

    def render(self, surf):
        offset_end = (Pos(self.offset) + Pos(surf.get_size())).t
        for line in range(Level.world_to_map(self.offset)[1],
                          clamp(Level.world_to_map(offset_end)[1] + 2, 0, self.size[1] - 1)):
            for block in range(Level.world_to_map(self.offset)[0],
                               clamp(Level.world_to_map(offset_end)[0] + 2, 0, self.size[0] - 1)):
                if self.grid[line][block].visible:
                    surf.blit(self.get_img_at((block, line)), self.map_to_world((block, line)) - self.offset)
