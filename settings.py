import pygame

from graphalama.buttons import CarouselSwitch
from graphalama.shapes import RoundedRect
from graphalama.constants import BOTTOM, WHITESMOKE

from widgets import MenuButton
from constants import LIGHT_DARK
from config import get_available_players, CONFIG, get_index_from_name, PLAYERS
from idle_screen import IdleScreen


class SettingsScreen(IdleScreen):
    def __init__(self, app):
        size = app.display.get_size()

        self.player_selector = CarouselSwitch(options=get_available_players,
                                              on_choice=SettingsScreen.player_setter,
                                              pos=(size[0] // 2, size[1] // 2 - 75),
                                              shape=RoundedRect((400, 75)),
                                              color=WHITESMOKE,
                                              bg_color=LIGHT_DARK,
                                              arrow_color=WHITESMOKE,
                                              anchor=BOTTOM)
        widgets = [
            MenuButton(app, (size[0] - 135, 100)),
            self.player_selector,
        ]

        self.player_selector.option_index = CONFIG.player

        super().__init__(app, widgets, (20, 10, 0))

    @staticmethod
    def player_setter(player):
        CONFIG.player = get_index_from_name(PLAYERS, player)
