from functools import partial

from graphalama.text import SimpleText
from graphalama.shapes import  Rectangle
from graphalama.font import default_font
from graphalama.colors import Gradient, MultiGradient
from graphalama.constants import (CENTER, NICE_BLUE, PURPLE, GREEN,
                                  Monokai, YELLOW, RED, TOP, WHITESMOKE, RAINBOW, LEFT, RIGHT, TRANSPARENT, LLAMA,
                                  TOPRIGHT)

from idle_screen import IdleScreen
from config import CONFIG
from constants import DARK
from widgets import Title, MenuButton


class StatisticsScreen(IdleScreen):
    def __init__(self, app):
        size = app.display.get_size()

        def stats(text, figure, n):
            y = size[1] // 2 + 100 * (n + 1)
            x = size[0] // 2 - 300
            text = SimpleText(text=text + ":",
                              pos=(x, y),
                              color=WHITESMOKE,
                              anchor=LEFT)
            figure = SimpleText(text=figure,
                                pos=(x + 600, y),
                                color=(255, 165, 0),
                                anchor=RIGHT)

            return text, figure

        widgets = [
            Title("Statistics, math, numbers, science", size, font_size=110),
            MenuButton(app, (size[0] - 135, 250)),
            *stats("Death count", self.get_total_deaths(), 0),
            *stats("Average death per level", self.get_avg_deaths_per_lvl(), 1),
            *stats("Total completion", self.get_total_completion(), 2),
            *stats("Автомат Калашникова picked up", self.get_nb_ak47(), 3)
        ]

        super().__init__(app, widgets, (20, 10, 0))

    def format_stat(self, text, number):
        number = str(number)
        return "{} {:.>{dots}} {}".format(text, "", number,
                                         dots=40 - len(text) -len(number))

    @staticmethod
    def get_total_deaths():
        total = 0
        for level in CONFIG.levels_stats:
            total += CONFIG.levels_stats[level][0]
        return total

    @staticmethod
    def get_avg_deaths_per_lvl():
        return StatisticsScreen.get_total_deaths() // len(CONFIG.levels_stats)

    @staticmethod
    def get_total_completion():
        levels_completed = 0
        for level in CONFIG.levels_stats:
            if CONFIG.levels_stats[level][1] != -1:
                levels_completed += 1
        return str(levels_completed * 100 / len(CONFIG.levels_stats)) + "%"

    @staticmethod
    def get_nb_ak47():
        return 0
