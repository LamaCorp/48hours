import pygame 

from physics import Body, AABB

class Player(Body):
    def __init__(self, start_pos=(0, 0)):
        shape = AABB(start_pos, (35, 32))
        super().__init__(shape)

        self.img = pygame.image.load('assets/player/lama.png').convert()
        self.img = pygame.transform.scale(self.img, (35, 32))
        self.img.set_colorkey((255, 0, 255))

    def render(self, surf, offset=(0, 0)):
        surf.blit(self.img, self.topleft + offset)