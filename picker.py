import pygame

from graphalama.app import Screen

from graphalama.buttons import CarouselSwitch
from graphalama.shapes import RoundedRect
from graphalama.constants import BOTTOM, WHITESMOKE

from widgets import MenuButton, SettingsButton, PlayButton
from constants import LIGHT_DARK
from config import get_available_levels, LevelConfig


class PickerScreen(Screen):
    FPS = 60

    def __init__(self, app):
        size = app.display.get_size()
        self.play_button = PlayButton(app, (size[0] // 2, size[1] // 2 + 75))
        self.selector = CarouselSwitch(options=get_available_levels,
                                       on_choice=PickerScreen.level_setter,
                                       pos=(size[0] // 2, size[1] // 2 - 75),
                                       shape=RoundedRect((400, 75)),
                                       color=WHITESMOKE,
                                       bg_color=LIGHT_DARK,
                                       arrow_color=WHITESMOKE,
                                       anchor=BOTTOM)
        widgets = [
            MenuButton(app, (size[0] - 365, 100)),
            SettingsButton(app, (size[0] - 135, 100)),
            self.selector,
            self.play_button,
        ]
        self.selector.option_index = 1

        self.lama_logo = pygame.image.load('assets/players/lama_normal.png').convert()
        for _ in range(4):
            self.lama_logo = pygame.transform.scale2x(self.lama_logo)
        self.lama_logo_left = pygame.transform.flip(self.lama_logo, True, False)
        self.lama_logo.set_colorkey((255, 0, 255))
        self.lama_logo_left.set_colorkey((255, 0, 255))

        super().__init__(app, widgets, (20, 10, 0))

    @staticmethod
    def level_setter(level):
        LevelConfig.chosen_level = level

    def draw_background(self, display):
        super().draw_background(display)

        rect = self.lama_logo.get_rect()
        ss = self.app.display.get_size()
        rect.center = (ss[0] // 5, ss[1] // 2)
        display.blit(self.lama_logo, rect)
        rect.center = (ss[0] * 4/5, ss[1] // 2)
        display.blit(self.lama_logo_left, rect)
