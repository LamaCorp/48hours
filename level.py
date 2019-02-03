import json
import os
from functools import lru_cache
from typing import List

from blocks import Block, Stone
from constants import MAPS_FOLDER, START
from config import LEVELS, CONFIG, get_index_from_name
from entities import Spawn, Object, AK47
from physics import Space, Pos, clamp, Projectile


class Level:
    OFFSET_THRESHOLD = 40 / 100

    def __init__(self):
        self.num = 0
        self.space = Space(self, gravity=(0, 1))
        self.size = Pos(0, 0)
        self.grid = []  # type: List[List[Block]]
        self.objects = []
        self.start = (0, 0)  # Where the players has to spawn, map coordinates
        self.offset = Pos(0, 0)  # Where we start to draw the map, world coordinates
        self.screen_size = (0, 0)
        self.over = False
        self.to_reset = False
        self.expolding = False
        self.expolsion_heads = []

    def __str__(self):
        return "\n".join([
            "".join(c.character for c in line) for line in self.grid
        ])

    @property
    def world_start(self):
        return self.map_to_world(self.start)

    @staticmethod
    def map_to_world(map_pos):
        return Pos(map_pos[0] * Block.DEFAULT_BLOCK_SIZE, map_pos[1] * Block.DEFAULT_BLOCK_SIZE)

    @staticmethod
    def world_to_map(world_pos):
        return (Pos(world_pos) // Block.DEFAULT_BLOCK_SIZE).i

    def map_to_display(self, map_pos):
        return Pos(map_pos[0] * Block.DEFAULT_BLOCK_SIZE - self.offset.x,
                   map_pos[1] * Block.DEFAULT_BLOCK_SIZE - self.offset.y)

    def display_to_map(self, display_pos):
        return Pos((display_pos[0] + self.offset.x) // Block.DEFAULT_BLOCK_SIZE,
                   (display_pos[1] + self.offset.y) // Block.DEFAULT_BLOCK_SIZE)

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
    @classmethod
    def load(cls, path, num=-1):
        try:
            level = cls.load_v1(path)
            level.path = path
            return level
        except:
            print('Can not load as v1')

        try:
            level = cls.load_v2(path, num)
            level.path = path
            return level
        except:
            print('Can not load as v2')
            raise

    @classmethod
    def load_v2(cls, path, num=-1, is_editor=False):
        with open(path, "r") as f:
            d = json.loads(f.read())

        size = Pos(d["size"])
        map = [
            [
                Block.new(c, (x, y))
                for x, c in enumerate(line)
            ]
            for y, line in enumerate(d["blocks"])
        ]
        objects = [Object.from_json(o) for o in d["objects"]]

        level = cls()
        level.size = size
        level.grid = map
        level.objects = objects

        # spawn
        for obj in objects:
            if isinstance(obj, Spawn):
                level.start = obj.pos
            elif isinstance(obj, Projectile):
                print(level.num)
                if not is_editor and isinstance(obj, AK47) and CONFIG.levels_stats[str(num)][2] >= 1:
                    pass
                else:
                    level.spawn(obj)
                    print(obj)

        return level

    def save(self, path):
        d = {}
        d["size"] = self.size.ti
        d["blocks"] = str(self).splitlines(keepends=False)
        d["objects"] = [obj.save() for obj in self.objects]
        d["version"] = 2

        s = json.dumps(d, indent=4)
        with open(path, "w") as f:
            f.write(s)

    @classmethod
    def load_num(cls, num):
        path = os.path.join(MAPS_FOLDER, LEVELS[str(num)][0])
        level = cls.load(path, num)
        level.num = num
        return level

    @classmethod
    def load_v1(cls, path):  # TODO: may we improve this?
        level = cls()

        with open(path, 'r') as map_file:
            height, width = list(map(int, map_file.readline().split()))
            level.size = Pos(width, height)
            for h in range(height):
                line = list(map_file.readline().strip())
                for i in range(len(line)):
                    if line[i] == START:
                        level.start = (i, h)
                    line[i] = Block.new(line[i], (i, h))
                level.grid.append(line)

        return level

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
        if self.expolding:
            self.explosion_logic()
            return

        offset = self.world_to_map(self.offset)
        offset_end = (offset + self.world_to_map(self.screen_size)).i

        for line in range(clamp(offset.y - 20, 0, self.size[1] - 1),
                          clamp(offset_end.y+ 20, 0, self.size[1] - 1)):
            for block in range(clamp(offset.x - 20, 0, self.size[0] - 1),
                               clamp(offset_end.x + 20, 0, self.size[0] - 1)):
                block = self.grid[line][block]
                block.internal_logic(self)

    def render(self, surf):
        self.screen_size = Pos(surf.get_size())
        offset = self.world_to_map(self.offset)
        offset_end = (offset + self.world_to_map(self.screen_size))

        for line in range(clamp(offset.y, 0, self.size[1] - 1),
                          clamp(offset_end.y + 2, 0, self.size[1])):
            for block in range(clamp(offset.x, 0, self.size[0] - 1),
                               clamp(offset_end.x + 2, 0, self.size[0])):
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

    def explode(self, start_pos):
        self.over = True
        self.expolding = True
        self.expolsion_heads.append(start_pos)

    def explosion_logic(self):
        for head in self.expolsion_heads:
            self.grid[head[1]][head[0]].explode()
