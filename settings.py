import os

import pygame

from graphalama.buttons import CarouselSwitch, Button
from graphalama.shapes import RoundedRect
from graphalama.text import SimpleText
from graphalama.constants import BOTTOM, WHITESMOKE, Monokai

from widgets import MenuButton, Title
from constants import LIGHT_DARK, PLAYER_FOLDER, KEY_BIND
from config import get_available_players, CONFIG, get_index_from_name, PLAYERS
from idle_screen import IdleScreen


class SettingsScreen(IdleScreen):
    def __init__(self, app):
        size = app.display.get_size()

        self.player_selector = CarouselSwitch(options=get_available_players,
                                              on_choice=self.player_setter,
                                              pos=(size[0] // 2, size[1] // 2 - 75),
                                              shape=RoundedRect((400, 75)),
                                              color=WHITESMOKE,
                                              bg_color=LIGHT_DARK,
                                              arrow_color=WHITESMOKE,
                                              anchor=BOTTOM)
        widgets = [
            Title("Settings", size),
            MenuButton(app, (size[0] - 135, 250)),
            SimpleText(text="Get more Kalachnikovs to unlock more!",
                       pos=(size[0] // 2, size[1] // 2 + 25),
                       color=WHITESMOKE,
                       anchor=BOTTOM),
            self.player_selector,
            Button(text="Key Bindings",
                   function=lambda: app.set_screen(KEY_BIND),
                   shape=RoundedRect((250, 50), 100),
                   color=Monokai.PINK,
                   bg_color=(200, 200, 200, 72),
                   pos=(size[0] // 2, size[1] // 2 + 100),
                   anchor=BOTTOM),

        ]

        self.player_selector.option_index = CONFIG.player
        self.img_preview = pygame.image.load(os.path.join(PLAYER_FOLDER,
                                                          PLAYERS[self.player_selector.option_index][0])).convert()
        self.img_preview.set_colorkey((255, 0, 255))
        for _ in range(3):
            self.img_preview = pygame.transform.scale2x(self.img_preview)

        super().__init__(app, widgets, (20, 10, 0))

    def player_setter(self, player):
        CONFIG.player = get_index_from_name(PLAYERS, player)
        self.img_preview = pygame.image.load(os.path.join(PLAYER_FOLDER,
                                                          PLAYERS[self.player_selector.option_index][0])).convert()
        self.img_preview.set_colorkey((255, 0, 255))
        for _ in range(3):
            self.img_preview = pygame.transform.scale2x(self.img_preview)

    def render(self, display):
        super().render(display)

        rect = self.img_preview.get_rect()
        size = self.app.display.get_size()
        rect.center = (size[0] // 2, size[1] // 2 + 300)
        display.blit(self.img_preview, rect)
