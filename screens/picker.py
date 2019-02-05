import os

import pygame
from graphalama.buttons import CarouselSwitch
from graphalama.colors import MultiGradient
from graphalama.core import Widget
from graphalama.text import SimpleText
from graphalama.shapes import RoundedRect, Rectangle
from graphalama.constants import BOTTOM, WHITESMOKE, LLAMA, CENTER, RIGHT, TOP, RAINBOW, LEFT
from graphalama.maths import Pos

from blocks import get_boom_img
from screens.widgets import MenuButton, SettingsButton, PlayButton, Title, SurfaceButton
from constants import LIGHT_DARK, GREY, ASSETS
from config import CONFIG, LEVELS, get_index_from_name, get_available_levels, LEVELS_GRAPHICAL_FOLDER
from screens.idle_screen import IdleScreen


class PickerScreen(IdleScreen):
    def __init__(self, app):
        size = app.display.get_size()

        # loading images
        self.ak47 = pygame.image.load(os.path.join(LEVELS_GRAPHICAL_FOLDER, "ak47.png")).convert()
        self.ak47.set_colorkey((255, 0, 255))
        for _ in range(2):
            self.ak47 = pygame.transform.scale2x(self.ak47)
        self.ak47 = pygame.transform.rotate(self.ak47, -30)

        self.deaths_img = pygame.image.load(os.path.join(ASSETS, 'skull.png')).convert()
        self.deaths_img = pygame.transform.scale2x(self.deaths_img)
        self.deaths_img.set_colorkey((255, 0, 255))

        self.timer_img = pygame.image.load(os.path.join(ASSETS, 'silver_clock.png')).convert()
        self.timer_img = pygame.transform.scale2x(self.timer_img)
        self.timer_img.set_colorkey((255, 0, 255))

        self.boom_img = pygame.transform.scale2x(get_boom_img(10))
        self.boom_img = get_boom_img(10)

        # creating widgets
        x = size[0] // 2
        # backgrounds
        self.bottom_band = Widget((x, size[1] + 1),
                                  shape=Rectangle((size[0] + 2, 75), border=1),
                                  bg_color=GREY,
                                  border_color=MultiGradient(*RAINBOW),
                                  anchor=BOTTOM)
        # principal buttons
        self.selector = CarouselSwitch(options=get_available_levels,
                                       on_choice=PickerScreen.level_setter,
                                       pos=(x, size[1] // 2 - 20),
                                       shape=RoundedRect((525, 75), 100),
                                       color=WHITESMOKE,
                                       bg_color=LIGHT_DARK,
                                       arrow_color=WHITESMOKE,
                                       anchor=BOTTOM)
        self.play_button = PlayButton(app, (x, size[1] // 2 + 20), anchor=TOP)
        menu = MenuButton(app, (size[0] - 45, 250), anchor=RIGHT)
        settings = SettingsButton(app, (menu.topleft.x - 20, 250), anchor=RIGHT)
        level_stats = CONFIG.levels_stats[str(self.selector.option_index)]

        # stats
        y = self.bottom_band.absolute_rect.centery
        self.deaths_text = SimpleText(text=self.death_count_text(level_stats[0]),
                                      pos=(10*2 + self.deaths_img.get_width(), y),
                                      color=WHITESMOKE,
                                      anchor=LEFT)
        self.best_time = SimpleText(text=self.time_text(level_stats[1]),
                                    pos=(x, y),
                                    color=WHITESMOKE,
                                    anchor=CENTER)
        self.exploded_blocks = SimpleText(text=self.blocks_exploded_text(level_stats[3]),
                                          pos=(size[0] - 10*2 - self.boom_img.get_width(), y),
                                          color=WHITESMOKE,
                                          anchor=RIGHT)

        widgets = [
            Title("Choose where you die", size),
            self.bottom_band,
            self.play_button,
            self.selector,
            self.deaths_text,
            self.best_time,
            self.exploded_blocks,
            settings,
            menu,
        ]

        self.selector.option_index = CONFIG.level

        super().__init__(app, widgets, (20, 10, 0))

    @staticmethod
    def level_setter(level):
        CONFIG.level = int(get_index_from_name(LEVELS, level))

    def death_count_text(self, n_death):
        return str(n_death)

    def time_text(self, seconds):
        if seconds < 0:
            return "Not finished"

        seconds, mili = divmod(seconds, 1)
        minutes, seconds = divmod(seconds, 60)

        mili = round(mili * 1000)
        seconds = int(seconds)
        minutes = int(minutes)
        if minutes:
            return "{:02}:{:02}.{:03}s".format(minutes, seconds, mili)
        else:
            return "{:02}.{:03}s".format(seconds, mili)

    def blocks_exploded_text(self, n_blocks):
        return str(n_blocks)

    def internal_logic(self):
        level_stats = CONFIG.levels_stats[str(self.selector.option_index)]
        self.deaths_text.text = self.death_count_text(level_stats[0])
        self.best_time.text = self.time_text(level_stats[1])
        self.exploded_blocks.text = self.blocks_exploded_text(level_stats[3])

    def render(self, display):
        super().render(display)
        if CONFIG.levels_stats[str(CONFIG.level)][2] >= 1:
            rect = self.ak47.get_rect()
            rect.center = self.selector.absolute_topleft + Pos(self.selector.size[0] - 100, 10)
            display.blit(self.ak47, rect)

        size = self.app.display.get_size()
        y = self.bottom_band.absolute_rect.centery
        # death
        rect = self.deaths_img.get_rect()
        rect.midleft = 10, y
        display.blit(self.deaths_img, rect)
        # time
        rect = self.timer_img.get_rect()
        rect.midright = self.best_time.absolute_rect.left - 10, y
        display.blit(self.timer_img, rect)
        # explosions
        rect = self.boom_img.get_rect()
        rect.midright = (size[0] - 10, y)
        display.blit(self.boom_img, rect)

