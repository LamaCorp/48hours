import os

import pygame

from graphalama.buttons import Button
from graphalama.shapes import RoundedRect
from graphalama.text import SimpleText
from graphalama.constants import BOTTOM, WHITESMOKE, Monokai, CENTER

from widgets import MenuButton, Title
from constants import LIGHT_DARK, PLAYER_FOLDER, SETTINGS
from config import get_available_players, CONFIG, get_index_from_name, PLAYERS
from idle_screen import IdleScreen


class KeyBindingsScreen(IdleScreen):
    def __init__(self, app):
        size = app.display.get_size()

        widgets = [
            Button(text="Back",
                   function=lambda: app.set_screen(SETTINGS),
                   shape=RoundedRect((200, 50), 100),
                   color=Monokai.PINK,
                   bg_color=(200, 200, 200, 72),
                   pos=(size[0] // 2, size[1] - 100),
                   anchor=CENTER),
        ]

        super().__init__(app, widgets, (20, 10, 0))
