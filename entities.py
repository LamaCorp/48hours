import os
import random

import pygame

from constants import LEVELS_GRAPHICAL_FOLDER, DEFAULT_BLOCK_SIZE, BROCHETTE_VELOCITY
from config import get_available_blocks
from physics import AABB, Pos, Projectile


class Brochette(Projectile):
    deadly = True

    img = [
        pygame.transform.scale(pygame.image.load(os.path.join(LEVELS_GRAPHICAL_FOLDER,
                                                              brochette.lower())).convert(),
                               (DEFAULT_BLOCK_SIZE, DEFAULT_BLOCK_SIZE))
        for brochette in get_available_blocks("brochette")]

    def __init__(self, start_pos, direction=(0, 0)):
        shape = AABB(start_pos, (DEFAULT_BLOCK_SIZE - 2, DEFAULT_BLOCK_SIZE - 2))
        shape.topleft += (1, 1)
        # shape.center = start_pos
        super().__init__(shape, mass=0)
        self.velocity = Pos(direction) * BROCHETTE_VELOCITY
        self.sheet = random.choice(Brochette.img)
        self.sheet.set_colorkey((255, 0, 255))

    def internal_logic(self):
        if self.collisions:
            self.dead = True

    def render(self, surf, offset=(0, 0)):
        surf.blit(self.sheet, self.topleft + offset)

    def on_collision(self, level):
        del self

    def __del__(self):
        pass
        # TODO: delete me
