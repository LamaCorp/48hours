import os
import pygame
from physics import Space, Pos
from constants import LEVELS_GRAPHICAL_FOLDER, MAPS_FOLDER


class Block:
    BLOCKS = {
        "P": (None, False, True),
        ".": (None, False, False),
        # TODO: choose randomly between available textures
        # TODO: remove grass and automatically add grass when there is no block over it
        "G": (pygame.image.load(os.path.join(LEVELS_GRAPHICAL_FOLDER, "grass_000.png")).convert(), True, False),
        "D": (pygame.image.load(os.path.join(LEVELS_GRAPHICAL_FOLDER, "dirt_000.png")).convert(), True, False),
        "S": (pygame.image.load(os.path.join(LEVELS_GRAPHICAL_FOLDER, "stone_000.png")).convert(), True, False),
    }

    def __init__(self, character='.'):
        if not character in Block.BLOCKS:
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

    def map_to_world(self, map_pos):
        return Pos(map_pos) * 16

    def world_to_map(self, world_pos):
        return Pos(world_pos) // 16

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
