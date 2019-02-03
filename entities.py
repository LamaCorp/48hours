import os

import pygame

from constants import LEVELS_GRAPHICAL_FOLDER, DEFAULT_BLOCK_SIZE, BROCHETTE_VELOCITY
from physics import AABB, Pos, Projectile


class Brochette(Projectile):
    deadly = True

    img = pygame.image.load(os.path.join(LEVELS_GRAPHICAL_FOLDER, "brochette_1.png")).convert()  # TODO: choose between the two available textures
    img.set_colorkey((255, 0, 255))
    img = pygame.transform.scale(img, (DEFAULT_BLOCK_SIZE, DEFAULT_BLOCK_SIZE))

    def __init__(self, start_pos, direction=(0, 0)):
        shape = AABB(start_pos, (DEFAULT_BLOCK_SIZE - 2, DEFAULT_BLOCK_SIZE - 2))
        shape.topleft += (1, 1)
        # shape.center = start_pos
        super().__init__(shape, mass=0)
        self.velocity = Pos(direction) * BROCHETTE_VELOCITY

    def internal_logic(self):
        if self.collisions:
            self.dead = True

    def render(self, surf, offset=(0, 0)):
        surf.blit(Brochette.img, self.topleft + offset)

    def on_collision(self, level):
        del self

    def __del__(self):
        pass
        # TODO: delete me
