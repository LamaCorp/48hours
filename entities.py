import os
import random
from functools import lru_cache

import pygame

from constants import LEVELS_GRAPHICAL_FOLDER, DEFAULT_BLOCK_SIZE, BROCHETTE_VELOCITY, FRAME_BEFORE_DESPAWN
from config import get_available_blocks
from helper import classproperty
from physics import AABB, Pos, Projectile, CollisionType

SPAWN = "Spawn"


class Object:
    _img = None  # type: pygame.Surface
    img = _img

    type: str
    pos: (int, int)

    def __init__(self, pos=(0, 0), **kwargs):
        self.type = self.__class__.__name__
        self.pos = pos

    @classmethod
    def from_json(cls, d):
        type = d["type"]
        return OBJECTS[type](**d)

    def save(self):
        d = {
            "type": self.type,
            "pos": tuple(self.pos)
        }
        return d


class Spawn(Object):

    @classproperty
    def img(cls):
        if cls._img is None:
            img = pygame.Surface((DEFAULT_BLOCK_SIZE, DEFAULT_BLOCK_SIZE))
            img.set_colorkey((0, 0, 0))
            # red circle
            pygame.draw.circle(img, (255, 0, 0), (DEFAULT_BLOCK_SIZE // 2,) * 2,
                               (DEFAULT_BLOCK_SIZE // 4))

            cls._img = img
        return cls._img


class AK47(Object, Projectile):
    character = "K"
    deadly = False
    rotation = None

    def __init__(self, **kwargs):
        Object.__init__(self, **kwargs)

        shape = AABB(self.pos[0] * DEFAULT_BLOCK_SIZE, self.pos[1] * DEFAULT_BLOCK_SIZE,
                     DEFAULT_BLOCK_SIZE, DEFAULT_BLOCK_SIZE)
        Projectile.__init__(self, shape)

    @classproperty
    def img(cls):
        if cls._img is None:
            sheet = pygame.image.load(os.path.join(LEVELS_GRAPHICAL_FOLDER, "ak47.png")).convert()
            sheet.set_colorkey((255, 0, 255))
            sheet = pygame.transform.scale(sheet, (DEFAULT_BLOCK_SIZE, DEFAULT_BLOCK_SIZE))
            cls._img = sheet
        return cls._img

    def get_img(self, neigh, rotation):
        return self.img

    def render(self, surf, offset=(0, 0)):
        surf.blit(self.img, self.topleft + offset)


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

    @classmethod
    @lru_cache()
    def get_image(cls, rot, alpha, variant):
        img = pygame.transform.rotate(variant, rot)
        img.set_colorkey((255, 0, 255))
        img.set_alpha(round(alpha))
        return img

    def __init__(self, start_pos, physics=(0, Pos(0, 0))):
        shape = AABB(start_pos, (DEFAULT_BLOCK_SIZE - 2, DEFAULT_BLOCK_SIZE - 2))
        shape.topleft += (1, 1)
        # shape.center = start_pos
        super().__init__(shape, mass=0)
        self.velocity = physics[1] * BROCHETTE_VELOCITY
        self.rotation = physics[0] - 90
        self.variant = random.choice(self.img)
        self.ttl = FRAME_BEFORE_DESPAWN

    def render(self, surf, offset=(0, 0)):
        surf.blit(self.get_image(self.rotation, 255 * self.ttl / FRAME_BEFORE_DESPAWN, self.variant),
                  self.topleft + offset)

    def internal_logic(self):

        for colli in self.collisions:
            if colli.type == CollisionType.BLOCK:
                self.sleep = True

        if self.sleep:
            self.ttl -= 1
            if self.ttl <= 0:
                self.dead = True


OBJECTS = {
    SPAWN: Spawn,
    "AK47": AK47
}
