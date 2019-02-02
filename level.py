import os
import pygame
from physics import Space, Pos
from constants import LEVELS_GRAPHICAL_FOLDER, MAPS_FOLDER


class Block:
    DEFAULT_BLOCK_SIZE = 32
    BLOCKS = {
        "P": (None, False, True),
        ".": (None, False, False),
        # TODO: choose randomly between available textures
        # TODO: remove grass and automatically add grass when there is no block over it
        "G": (
             pygame.transform.scale(pygame.image.load(os.path.join(LEVELS_GRAPHICAL_FOLDER, "grass_000.png")).convert(),
                                    (DEFAULT_BLOCK_SIZE, DEFAULT_BLOCK_SIZE)),
             True,
             False
        ),
        "D": (
             pygame.transform.scale(pygame.image.load(os.path.join(LEVELS_GRAPHICAL_FOLDER, "dirt_000.png")).convert(),
                                    (DEFAULT_BLOCK_SIZE, DEFAULT_BLOCK_SIZE)),
             True,
             False
        ),
        "S": (
             pygame.transform.scale(pygame.image.load(os.path.join(LEVELS_GRAPHICAL_FOLDER, "stone_000.png")).convert(),
                                    (DEFAULT_BLOCK_SIZE, DEFAULT_BLOCK_SIZE)),
             True,
             False
        ),
    }

    def __init__(self, character='.'):
        if character not in Block.BLOCKS:
            raise Exception("Shit fuck")  # TODO: maybe be just an empty one
        self.block = Block.BLOCKS[character]
        self.img = self.block[0]
        self.solid = self.block[1]
        self.start = self.block[2]

    def render(self, surf, pos=None):
        if self.is_solid:
            surf.blit(self.img, pos)

    @property
    def is_solid(self):
        return self.solid

    @property
    def is_start(self):
        return self.start


class Level:
    def __init__(self, level='level_0'):
        self.name = level
        self.space = Space(gravity=(0, 1))
        self.grid = []
        self.start = (0, 0)
        self.load_level()

    @staticmethod
    def map_to_world(map_pos):
        return Pos(map_pos) * Block.DEFAULT_BLOCK_SIZE

    @staticmethod
    def world_to_map(world_pos):
        return Pos(world_pos) // Block.DEFAULT_BLOCK_SIZE

    @property
    def map_size(self):
        if len(self.grid) > 0:
            return len(self.grid), len(self.grid[0])
        else:
            return 0, 0

    @property
    def world_size(self):
        return Level.map_to_world(self.map_size)
    
    @property
    def size(self):
        return self.map_size

    def load_level(self):  # TODO: may we improve this?
        with open(os.path.join(MAPS_FOLDER, self.name + ".map"), 'r') as map_file:
            height, width = list(map(int, map_file.readline().split()))
            for h in range(height):
                line = list(map_file.readline().strip())
                for i in range(len(line)):
                    line[i] = Block(line[i])
                    if line[i].is_start:
                        self.start = (h, i)
                self.grid.append(line)

    def render(self, surf):
        for line in range(len(self.grid)):
            for block in range(len(self.grid[line])):
                self.grid[line][block].render(surf, self.map_to_world((block, line)))
