import json
import os
import random
import logging
from time import time
from typing import List

from blocks import Block, Stone, get_boom_img
from constants import MAPS_FOLDER, START
from config import LEVELS, CONFIG
from entities import Spawn, Object, AK47, Particle
from physics import Space, Pos, clamp, Projectile

LOGGER = logging.getLogger(__name__)


class Level:
    OFFSET_THRESHOLD = 40 / 100

    def __init__(self):
        LOGGER.info("Initialized new level")
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
        self.exploding = False
        self.to_explode = []
        self.exploded = []
        self.particles = []
        self.img_cache = {}

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

    def inside_map(self, map_pos):
        return 0 <= map_pos[0] < self.size.x and 0 <= map_pos[1] < self.size.y

    def inside_display(self, map_pos):
        world = self.map_to_world(map_pos)
        return (self.offset.x <= world.x < self.offset.x + self.screen_size[0] and
                self.offset.y <= world.y < self.offset.y + self.screen_size[1])

    def get_block(self, map_pos):
        x, y = map_pos
        if self.inside_map(map_pos):
            return self.grid[y][x]

        # TODO: this happens way to often. Why the fuck?!
        # LOGGER.debug(f"Level - get_block - {x}, {y} not inside map. Return a Stone by default.")
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

    def get_img_at(self, map_pos):
        if map_pos in self.img_cache:
            return self.img_cache[map_pos]

        neigh = "".join(self.get_block((map_pos[0] + dx, map_pos[1] + dy)).character
                        for dy in range(-1, 2)
                        for dx in range(-1, 2))
        block = self.get_block(map_pos)
        img = block.get_img(neigh, rotation=block.rotation)

        if not block.IGNORE_IMG_CACHE:
            self.img_cache[map_pos] = img

        return img

    @property
    def world_size(self):
        """(width, height), in pixels"""
        return Level.map_to_world(self.size)

    @classmethod
    def load(cls, path, num=-1):
        LOGGER.info(f"Starting to load map {num} from path {path}")
        try:
            level = cls.load_v1(path)
            level.path = path
            return level
        except Exception as e:
            LOGGER.info(f"Could not load map as v1. This is ok as we should only have v2 maps. "
                        f"To be deprecated. Here is the actual exception: {e}")

        try:
            level = cls.load_v2(path, num)
            level.path = path
            return level
        except Exception as e:
            LOGGER.critical(f"Could not load map as v2. Here is the exception: {e}")

    @classmethod
    def load_v2(cls, path, num=-1, is_editor=False):
        LOGGER.info(f"Trying to load #{num} as v2 from path {path}. is_editor: {is_editor}")
        with open(path, "r") as f:
            d = json.loads(f.read())
        LOGGER.info("Dict loaded: %s", d)

        size = Pos(d["size"])
        LOGGER.info("Level size: %s", size)
        map = [
            [
                Block.new(c, (x, y))
                for x, c in enumerate(line)
            ]
            for y, line in enumerate(d["blocks"])
        ]
        objects = [Object.from_json(o) for o in d["objects"]]
        LOGGER.info("Loaded %s objects", len(objects))

        level = cls()
        level.size = size
        level.grid = map
        level.objects = objects

        # spawn
        for obj in objects:
            if isinstance(obj, Spawn):
                level.start = obj.pos
                LOGGER.info("Spawn set at %s", obj.pos)
            elif isinstance(obj, Projectile):
                if not is_editor and isinstance(obj, AK47) and CONFIG.levels_stats[str(num)][2] >= 1:
                    pass
                else:
                    level.spawn(obj)

        LOGGER.info("Loaded as v2.")
        return level

    def save(self, path):
        LOGGER.info("Saving level to %s", path)
        d = dict()
        d["size"] = self.size.ti
        d["blocks"] = str(self).splitlines(keepends=False)
        d["objects"] = [obj.save() for obj in self.objects]
        d["version"] = 2
        LOGGER.info("Dictionary to save: %s", d)

        s = json.dumps(d, indent=4)
        with open(path, "w") as f:
            f.write(s)

    @classmethod
    def load_num(cls, num):
        LOGGER.info("Loading level from number: %s", num)
        path = os.path.join(MAPS_FOLDER, LEVELS[str(num)][0])
        LOGGER.info("Deduced level path: %s", path)
        level = cls.load(path, num)
        level.num = num
        return level

    @classmethod
    def load_v1(cls, path):  # TODO: may we improve this?
        level = cls()
        LOGGER.info(f"Trying to load as v1 from path {path}")

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

        LOGGER.warning(f"Loaded as v1. To be deprecated")
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
        if self.exploding:
            self.explosion_logic()
            return

        offset = self.world_to_map(self.offset)
        offset_end = (offset + self.world_to_map(self.screen_size)).i

        for line in range(clamp(offset.y - 20, 0, self.size[1] - 1),
                          clamp(offset_end.y + 20, 0, self.size[1] - 1)):
            for block in range(clamp(offset.x - 20, 0, self.size[0] - 1),
                               clamp(offset_end.x + 20, 0, self.size[0] - 1)):
                block = self.grid[line][block]
                block.internal_logic(self)

    def render(self, surf):
        if self.exploding:
            self.render_explode(surf)
            return

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
        LOGGER.info("Level: to_reset = True")
        self.to_reset = True

    def explode(self, start_pos):
        LOGGER.info("Starting to explode the level.")
        self.exploding = True
        self.to_explode = [
            b
            for line in self.grid
            for b in line
            if self.inside_display(b.pos) and b.visible
        ]
        self.exploded = []
        LOGGER.info(f"We're going to explode {len(self.to_explode)} blocks")

    def explosion_logic(self):

        for part in self.particles:
            part.internal_logic()
        self.particles = [p for p in self.particles if not p.dead and p.pos.y < self.screen_size[1]]

        for i in range(min(5, len(self.to_explode))):
            b = random.choice(self.to_explode)
            self.to_explode.remove(b)
            self.exploded.append(b)
            b.explode()
            # particles
            for i in range(5):
                angle = random.randint(0, 360)
                velocity = 25 * Pos.unit_y().rotate(angle)
                pos = self.map_to_display(b.pos)
                self.particles.append(Particle(pos, velocity, size=6))
            CONFIG.levels_stats[str(self.num)][3] += 1

        if not self.to_explode and not self.exploded and not self.particles:
            self.over = True
        return

    def render_explode(self, surf):
        t = time()

        for block in self.to_explode:
            world_pos = self.map_to_display(block.pos)
            surf.blit(self.get_img_at(block.pos), world_pos)

        for block in self.exploded[:]:
            world_pos = self.map_to_display(block.pos)
            if block.visible:
                surf.blit(self.get_img_at(block.pos), world_pos)
            surf.blit(get_boom_img(int(block.explode_frame)), world_pos - (16, 16))

            if block.explode_frame <= 15:
                block.explode_frame += 1/3
                if block.explode_frame > 4:
                    block.visible = False
            else:
                self.exploded.remove(block)

        for part in self.particles:
            part.render(surf)

        dx, dy = random.randint(-5, 6), random.randint(-5, 6)
        surf.scroll(dx, dy)
