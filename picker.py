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
        self.deaths_text = SimpleText(text="You died {} times".format(level_stats[0]),
                                      pos=(size[0] // 2, size[1] // 2 + 200),
                                      color=WHITESMOKE,
                                      anchor=CENTER)
        self.best_time = SimpleText(text="Your best time was {}".format("not recorded yet :/"
                                                                        if level_stats[1] == -1
                                                                        else datetime.timedelta(seconds=level_stats[1])),
                                    pos=(size[0] // 2, size[1] // 2 + 250),
                                    color=WHITESMOKE,
                                    anchor=CENTER)
        widgets = [
            MenuButton(app, (size[0] - 365, 100)),
            SettingsButton(app, (size[0] - 135, 100)),
            self.selector,
            self.play_button,
            self.level_text,
            self.deaths_text,
            self.best_time,
        ]

        self.selector.option_index = CONFIG.level

        super().__init__(app, widgets, (20, 10, 0))

    @staticmethod
    def level_setter(level):
        CONFIG.level = get_index_from_name(LEVELS, level)

    def internal_logic(self):
        level_stats = CONFIG.levels_stats[str(self.selector.option_index)]
        self.deaths_text.text = "You died {} times".format(level_stats[0])
        self.best_time.text = "Your best time was {}".format("not recorded yet :/"
                                                             if level_stats[1] == -1
                                                             else datetime.timedelta(seconds=level_stats[1]))
