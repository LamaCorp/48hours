import os
from functools import lru_cache
from typing import List

from blocks import Block, Stone
from constants import MAPS_FOLDER, START
from config import LEVELS
from physics import Space, Pos, clamp


class Level:
    OFFSET_THRESHOLD = 40 / 100

    def __init__(self, level=0):
        self.num = level
        self.space = Space(self, gravity=(0, 1))
        self.size = Pos(0, 0)
        self.grid = []  # type: List[List[Block]]
        self.start = (0, 0)  # Where the players has to spawn, map coordinates
        self.offset = Pos(0, 0)  # Where we start to draw the map, world coordinates
        self.load_level()
        self.screen_size = (0, 0)
        self.over = False
        self.to_reset = False

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
        with open(os.path.join(MAPS_FOLDER, LEVELS[self.num][0]), 'r') as map_file:
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

        for proj in self.space.projectiles:
            proj.render(surf, -self.offset)

    def spawn(self, body):
        self.space.add(body)

    def reset(self):
        self.to_reset = True

    def explode(self):
        # TODO
        self.over = True
