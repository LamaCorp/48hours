import pygame

from graphalama.buttons import CarouselSwitch
from graphalama.shapes import RoundedRect
from graphalama.constants import BOTTOM, WHITESMOKE

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

        self.selector.option_index = CONFIG.level

        super().__init__(app, widgets, (20, 10, 0))

    @staticmethod
    def level_setter(level):
        CONFIG.level = get_index_from_name(LEVELS, level)
