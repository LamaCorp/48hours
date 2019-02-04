from graphalama.text import SimpleText
from graphalama.constants import (WHITESMOKE, LEFT, RIGHT)
from idle_screen import IdleScreen
from config import CONFIG, get_nb_ak47
from widgets import Title, MenuButton, Segment


class StatisticsScreen(IdleScreen):
    def __init__(self, app):
        size = app.display.get_size()

        def stats(text, figure, n):
            y = size[1] // 2 + 100 * (n + 1)
            x = size[0] // 2 - 300
            text = SimpleText(text=text,
                              pos=(x, y),
                              color=WHITESMOKE,
                              anchor=LEFT)
            figure = SimpleText(text=figure,
                                pos=(x + 600, y),
                                color=(255, 165, 0),
                                anchor=RIGHT)
            segm = Segment(text.absolute_rect.bottomright, figure.absolute_rect.bottomleft, (100, 100, 100))
            segm.pos = (segm.pos[0], segm.pos[1] - 6)

            return text, figure, segm

        widgets = [
            Title("Statistics, math, numbers, science", size, font_size=110),
            *stats("Death count", self.get_total_deaths(), 0),
            *stats("Average death per level", self.get_avg_deaths_per_lvl(), 1),
            *stats("Total blocks exploded", self.get_total_blocks_exploded(), 2),
            *stats("Total completion", self.get_total_completion(), 3),
            *stats("Автомат Калашникова picked up", get_nb_ak47(), 4),
            MenuButton(app, (size[0] - 135, 250)),
        ]

        super().__init__(app, widgets, (20, 10, 0))

    def format_stat(self, text, number):
        number = str(number)
        return "{} {:.>{dots}} {}".format(text, "", number,
                                          dots=40 - len(text) - len(number))

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

        percent = levels_completed * 100 / len(CONFIG.levels_stats)
        return f"{int(percent)}%"

    @staticmethod
    def get_total_blocks_exploded():
        total = 0
        for level in CONFIG.levels_stats:
            total += CONFIG.levels_stats[level][3]
        return total
