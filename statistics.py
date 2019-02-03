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
        widgets = [
            SimpleText(text="Statistics, math, numbers, science",
                       pos=(size[0] / 2, 50),
                       shape=Rectangle((size[0] + 2, 133), border=1),
                       color=MultiGradient(*RAINBOW),
                       bg_color=DARK + (172,),
                       border_color=MultiGradient(*RAINBOW),
                       font=default_font(110),
                       anchor=TOP),
            MenuButton(app, (size[0] - 135, 250)),
            SimpleText(text="{:>30}: {:>4}".format("Total deaths", self.get_total_deaths()),
                       pos=(size[0] // 2, size[1] // 2 - 200),
                       color=WHITESMOKE),
            SimpleText(text="{:>30}: {:>4}".format("Average deaths per level", self.get_avg_deaths_per_lvl()),
                       pos=(size[0] // 2, size[1] // 2 - 100),
                       color=WHITESMOKE),
            SimpleText(text="{:>30}: {:>4}".format("Total completion", self.get_total_completion()),
                       pos=(size[0] // 2, size[1] // 2),
                       color=WHITESMOKE),
            SimpleText(text="{:>30}: {:>4}".format("Автомат Калашникова picked up", self.get_nb_ak47()),
                       pos=(size[0] // 2, size[1] // 2 + 100),
                       color=WHITESMOKE),
        ]

        super().__init__(app, widgets, (20, 10, 0))

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
