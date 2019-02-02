import os
import random
import pygame
from physics import Space, Pos, AABB, clamp
from constants import LEVELS_GRAPHICAL_FOLDER, MAPS_FOLDER
from config import get_available_blocks


class Block:
    DEFAULT_BLOCK_SIZE = 32
    BLOCKS = {
        "P": [(None, False, True)],
        ".": [(None, False, False)],
        # TODO: choose randomly between available textures
        # TODO: remove grass and automatically add grass when there is no block over it
        "G": [(pygame.transform.scale(pygame.image.load(os.path.join(LEVELS_GRAPHICAL_FOLDER, path.lower())).convert(),
                                      (DEFAULT_BLOCK_SIZE, DEFAULT_BLOCK_SIZE)),
               True, False)
              for path in get_available_blocks("grass")],
        "D": [(pygame.transform.scale(pygame.image.load(os.path.join(LEVELS_GRAPHICAL_FOLDER, path.lower())).convert(),
                                      (DEFAULT_BLOCK_SIZE, DEFAULT_BLOCK_SIZE)),
               True, False)
              for path in get_available_blocks("dirt")],
        "S": [(pygame.transform.scale(pygame.image.load(os.path.join(LEVELS_GRAPHICAL_FOLDER, path.lower())).convert(),
                                      (DEFAULT_BLOCK_SIZE, DEFAULT_BLOCK_SIZE)),
               True, False)
              for path in get_available_blocks("stone")],
    }

    def __init__(self, character='.'):
        if character not in Block.BLOCKS:
            raise Exception("Shit fuck")  # TODO: maybe be just an empty one
        self.block = random.choice(Block.BLOCKS[character])
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
    OFFSET_THRESHOLD = 40 / 100

    def __init__(self, level='level_0'):
        self.name = level
        self.space = Space(gravity=(0, 1))
        self.grid = []
        self.start = (0, 0)  # Where the player has to spawn, map coordinates
        self.offset = Pos(0, 0)  # Where we start to draw the map, world coordinates
        self.load_level()

        self.space.add(*self.collision_rects())

    @property
    def world_start(self):
        return self.map_to_world(self.start)

    @staticmethod
    def map_to_world(map_pos):
        return Pos(map_pos) * Block.DEFAULT_BLOCK_SIZE

    @staticmethod
    def world_to_map(world_pos):
        return (Pos(world_pos) // Block.DEFAULT_BLOCK_SIZE).i

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
        with open(os.path.join(MAPS_FOLDER, self.name.lower()), 'r') as map_file:
            height, width = list(map(int, map_file.readline().split()))
            for h in range(height):
                line = list(map_file.readline().strip())
                for i in range(len(line)):
                    line[i] = Block(line[i])
                    if line[i].is_start:
                        self.start = (i, h)
                self.grid.append(line)

    def update_offset(self, player_pos, screen_size):
        player_pos = Pos(player_pos) - Pos(self.offset)
        print("player", player_pos)
        print("offset", self.offset)
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
                                self.world_size[1] - screen_size[0] - Block.DEFAULT_BLOCK_SIZE),
                          clamp(self.offset[1],
                                Block.DEFAULT_BLOCK_SIZE,
                                self.world_size[0] - screen_size[1] - Block.DEFAULT_BLOCK_SIZE))

    def render(self, surf):
        offset_end = (Pos(self.offset) + Pos(surf.get_size())).t
        for line in range(Level.world_to_map(self.offset)[1],
                          clamp(Level.world_to_map(offset_end)[1] + 2, 0, self.map_size[0])):
            for block in range(Level.world_to_map(self.offset)[0],
                               clamp(Level.world_to_map(offset_end)[0] + 2, 0, self.map_size[1])):
                self.grid[line][block].render(surf, self.map_to_world((block, line)) - self.offset)

    def collision_rects(self):
        # we sort them by Y then X
        positions = [(y, x)
                     for y, line in enumerate(self.grid)
                     for x, tile in enumerate(line)
                     if tile.solid]
        positions.sort()

        tile_size = Block.DEFAULT_BLOCK_SIZE

        # so we can have line rects easily
        line_rects = []
        first = positions[0]
        last = positions[0]
        for pos in positions[1:]:
            if pos[0] == last[0] and pos[1] == last[1] + 1:
                # just after on the same line : we expand the block
                last = pos
            else:
                # end of last block
                size = last[1] - first[1] + 1
                x = first[1] * tile_size
                y = first[0] * tile_size
                w = size * tile_size
                h = tile_size
                line_rects.append(AABB(x, y, w, h))

                # we start a new block
                first = pos
                last = pos

        # we add the last block too
        size = last[1] - first[1] + 1
        x = first[1] * tile_size
        y = first[0] * tile_size
        w = size * tile_size
        h = tile_size
        line_rects.append(AABB(x, y, w, h))

        # todo: merge lines with the same width
        return line_rects
