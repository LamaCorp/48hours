import os
import random
from functools import lru_cache

import pygame
from graphalama.colors import mix

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
                     *self.img.get_size())
        Projectile.__init__(self, shape, mass=0)

    @classproperty
    def img(cls):
        if cls._img is None:
            # size = (32, 10)
            sheet = pygame.image.load(os.path.join(LEVELS_GRAPHICAL_FOLDER, "ak47.png")).convert()
            sheet.set_colorkey((255, 0, 255))
            # sheet = pygame.transform.scale(sheet, (DEFAULT_BLOCK_SIZE, DEFAULT_BLOCK_SIZE))
            cls._img = sheet
        return cls._img

    @classmethod
    @lru_cache(maxsize=2)
    def get_img(cls, flipped=False):
        if flipped:
            return pygame.transform.flip(cls.img, True, False)
        return cls.img

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

class Particle:
    def __init__(self, pos, velocity=(0, 0), acceleration=(0, 1), friction=0.1, life_time: int=60, size=3,
                 color=(255, 165, 0), color_shift=(80, 00, 0)):
        """Create a particle with a constant acceleration"""
        self.pos = Pos(pos)
        self.velocity = Pos(velocity)
        self.acceleration = Pos(acceleration)
        self.friction = friction
        self.life_time = life_time
        self.age = 0
        self.color = color
        self.color_shift = color_shift
        self.size = size
        self.dead = False

    def internal_logic(self):
        self.velocity += self.acceleration - self.friction * self.velocity
        self.pos += self.velocity
        self.age += 1
        if self.age > self.life_time:
            self.dead = True

    def render(self, surf: pygame.Surface):
        life_prop = 1 - self.age / self.life_time
        color = mix(self.color, self.color_shift, life_prop)

        rect = (self.pos, (self.size, self.size))
        surf.fill(color, rect)

        # img = self.get_img_surf(self.size, color, 255 * life_prop)
        # surf.blit(img, self.pos)

    @lru_cache()
    def get_img_surf(self, size, color, alpha):
        img = pygame.Surface((size, size))
        img.fill(color)
        # img.set_alpha(round(alpha))
        return img



OBJECTS = {
    SPAWN: Spawn,
    "AK47": AK47
}
