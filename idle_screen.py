import os
import pygame

from graphalama.app import Screen

from constants import PLAYER_FOLDER


class IdleScreen(Screen):
    FPS = 60

    def __init__(self, app, widgets=(), bg_color=()):
        self.lama_logo = pygame.image.load(os.path.join(PLAYER_FOLDER, "lama_normal.png")).convert()
        self.lama_logo.set_colorkey((255, 0, 255))
        for _ in range(4):
            self.lama_logo = pygame.transform.scale2x(self.lama_logo)
        self.lama_logo_left = pygame.transform.flip(self.lama_logo, True, False)
        super().__init__(app=app, widgets=widgets, bg_color=bg_color)
    
    def draw_background(self, display):
        super().draw_background(display)
        self.draw_lamas(display)

    def draw_lamas(self, display):
        rect = self.lama_logo.get_rect()
        size = self.app.display.get_size()
        rect.center = (size[0] // 5, size[1] // 2)
        display.blit(self.lama_logo, rect)
        rect.center = (size[0] * 4/5, size[1] // 2)
        display.blit(self.lama_logo_left, rect)
