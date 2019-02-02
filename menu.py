import pygame
from graphalama.app import Screen

from constants import SETTINGS, PICKER
from widgets import Title, PickerButton, SettingsButton, QuitButton

class MenuScreen(Screen):
    FPS = 30

    def __init__(self, app):
        size = app.display.get_size()
        widgets = [
            Title("Llama destroys the world", size),
            PickerButton(app, (size[0] // 2, size[1] // 2 - 65)),
            SettingsButton(app, (size[0] // 2, size[1] // 2)),
            QuitButton(app, (size[0] // 2, size[1] // 2 + 65)),
        ]

        self.lama_logo = pygame.image.load('assets/player/lama.png').convert()
        for _ in range(4):
            self.lama_logo = pygame.transform.scale2x(self.lama_logo)
        self.lama_logo_left = pygame.transform.flip(self.lama_logo, True, False)
        self.lama_logo.set_colorkey((255, 0, 255))
        self.lama_logo_left.set_colorkey((255, 0, 255))

        super().__init__(app, widgets, (20, 10, 0))

    def draw_background(self, display):
        super().draw_background(display)

        rect = self.lama_logo.get_rect()
        ss = self.app.display.get_size()
        rect.center = (ss[0] // 5, ss[1] // 2)
        display.blit(self.lama_logo, rect)
        rect.center = (ss[0] * 4/5, ss[1] // 2)
        display.blit(self.lama_logo_left, rect)


