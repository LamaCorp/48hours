import os
import random

import pygame

from constants import LEVELS_GRAPHICAL_FOLDER, DEFAULT_BLOCK_SIZE, BROCHETTE_VELOCITY
from config import get_available_blocks
from helper import classproperty
from physics import AABB, Pos, Projectile


class Brochette(Projectile):
    deadly = True
    _img = None

    @classproperty
    def img(cls):
        if cls._img is None:
            cls._img = [
            pygame.transform.scale(pygame.image.load(os.path.join(LEVELS_GRAPHICAL_FOLDER,
                                                                  brochette.lower())).convert(),
                                   (DEFAULT_BLOCK_SIZE, DEFAULT_BLOCK_SIZE))
            for brochette in get_available_blocks("brochette")]
        return cls._img

    def __init__(self, start_pos, physics=(0, Pos(0, 0))):
        shape = AABB(start_pos, (DEFAULT_BLOCK_SIZE - 2, DEFAULT_BLOCK_SIZE - 2))
        shape.topleft += (1, 1)
        # shape.center = start_pos
        super().__init__(shape, mass=0)
        self.velocity = physics[1] * BROCHETTE_VELOCITY
        self.rotation = physics[0] - 90
        self.sheet = pygame.transform.rotate(random.choice(Brochette.img), self.rotation)
        self.sheet.set_colorkey((255, 0, 255))
        self.ttl = 500

    def render(self, surf, offset=(0, 0)):
        surf.blit(self.sheet, self.topleft + offset)

    def internal_logic(self):
        self.ttl -= 1
        if self.ttl <= 0:
            self.dead = True


class AK47(Projectile):
    character = "K"
    deadly = False
    solid = False
    visible = True
    rotation = None
    _sheet = None

    @classproperty
    def sheet(cls):
        if cls._sheet is None:
            sheet = pygame.image.load(os.path.join(LEVELS_GRAPHICAL_FOLDER, "ak47.png")).convert()
            sheet.set_colorkey((255, 0, 255))
            sheet = pygame.transform.scale(sheet, (DEFAULT_BLOCK_SIZE, DEFAULT_BLOCK_SIZE))
            cls._sheet = sheet
        return cls._sheet

    def get_img(self, neigh, rotation):
        return self.sheet

    def on_collision(self, level):
        self.dead = True
        self.visible = False

    def internal_logic(self, level):
        pass
