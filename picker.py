import datetime

from graphalama.buttons import CarouselSwitch
from graphalama.text import SimpleText
from graphalama.shapes import RoundedRect
from graphalama.constants import BOTTOM, WHITESMOKE, LLAMA, CENTER

from widgets import MenuButton, SettingsButton, PlayButton
from constants import LIGHT_DARK
from config import CONFIG, LEVELS, get_index_from_name, get_available_levels
from idle_screen import IdleScreen


class PickerScreen(IdleScreen):
    def __init__(self, app):
        size = app.display.get_size()
        self.play_button = PlayButton(app, (size[0] // 2, size[1] // 2 + 75))
        self.selector = CarouselSwitch(options=get_available_levels,
                                       on_choice=PickerScreen.level_setter,
                                       pos=(size[0] // 2, size[1] // 2 - 75),
                                       shape=RoundedRect((525, 75)),
                                       color=WHITESMOKE,
                                       bg_color=LIGHT_DARK,
                                       arrow_color=WHITESMOKE,
                                       anchor=BOTTOM)
        level_stats = CONFIG.levels_stats[str(self.selector.option_index)]
        self.level_text = SimpleText(text="In this level",
                                     pos=(size[0] // 2, size[1] // 2 + 150),
                                     color=LLAMA,
                                     anchor=CENTER)

        self.deaths_text = SimpleText(text=self.death_count_text(level_stats[0]),
                                      pos=(size[0] // 2, size[1] // 2 + 200),
                                      color=WHITESMOKE,
                                      anchor=CENTER)
        self.best_time = SimpleText(text=self.time_text(level_stats[1]),
                                    pos=(size[0] // 2, size[1] // 2 + 250),
                                    color=WHITESMOKE,
                                    anchor=CENTER)
        self.exploded_blocks = SimpleText(text=self.blocks_exploded_text(level_stats[3]),
                                          pos=(size[0] // 2, size[1] // 2 + 300),
                                          color=WHITESMOKE,
                                          anchor=CENTER)
        widgets = [
            self.play_button,
            self.selector,
            self.level_text,
            self.deaths_text,
            self.best_time,
            self.exploded_blocks,
            MenuButton(app, (size[0] - 365, 100)),
            SettingsButton(app, (size[0] - 135, 100)),
        ]

        self.selector.option_index = CONFIG.level

        super().__init__(app, widgets, (20, 10, 0))

    @staticmethod
    def level_setter(level):
        CONFIG.level = int(get_index_from_name(LEVELS, level))

    def death_count_text(self, n_death):
        death_count = "You'll die soon..."
        if n_death == 1:
            death_count = "You died once"
        elif n_death == 2:
            death_count = "You died twice"
        elif n_death > 2:
            death_count = f"You died {n_death} times"

        return death_count

    def time_text(self, seconds):
        if seconds < 0:
            return "Your best time was not recorded yet :/"

        seconds, mili = divmod(seconds, 1)
        minutes, seconds = divmod(seconds, 60)

        mili = round(mili * 1000)
        seconds = int(seconds)
        minutes = int(minutes)
        if minutes:
            return "Your best time is {:02}:{:02}.{:03}s".format(minutes, seconds, mili)
        else:
            return "Your best time is {:02}.{:03}s".format(seconds, mili)

    def blocks_exploded_text(self, n_blocks):
        block_count = "You didn't explode any blocks"
        if n_blocks == 1:
            block_count = f"You exploded {n_blocks} block"
        elif n_blocks > 1:
            block_count = f"You exploded {n_blocks} blocks"
        return block_count

    def internal_logic(self):
        level_stats = CONFIG.levels_stats[str(self.selector.option_index)]
        self.deaths_text.text = self.death_count_text(level_stats[0])
        self.best_time.text = self.time_text(level_stats[1])
        self.exploded_blocks.text = self.blocks_exploded_text(level_stats[3])

