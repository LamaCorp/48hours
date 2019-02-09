import os
import pygame
import logging

from graphalama.buttons import CarouselSwitch, Button, CheckBox
from graphalama.colors import MultiGradient
from graphalama.maths import Pos
from graphalama.shapes import RoundedRect
from graphalama.text import SimpleText
from graphalama.constants import BOTTOM, WHITESMOKE, Monokai, RIGHT, RAINBOW, LEFT, LLAMA

from screens.widgets import MenuButton, Title, UnderlinedSimpleText
from constants import LIGHT_DARK, PLAYER_FOLDER, KEY_BIND, DARK_GREY, USER_AGREE
from config import get_available_players, CONFIG, get_index_from_name, PLAYERS
from screens.idle_screen import IdleScreen

LOGGER = logging.getLogger(__name__)


class SettingsScreen(IdleScreen):
    def __init__(self, app):
        LOGGER.info("Starting a SettingsScreen")
        size = app.display.get_size()

        self.player_selector = CarouselSwitch(options=get_available_players,
                                              on_choice=self.player_setter,
                                              pos=(size[0] // 2, size[1] // 2 + 125),
                                              shape=RoundedRect((400, 75), rounding=50),
                                              color=WHITESMOKE,
                                              bg_color=LIGHT_DARK,
                                              arrow_color=WHITESMOKE,
                                              anchor=BOTTOM)

        # Crash Reports
        text = "Send anonymous crash reports, so we can make this game even better!"
        bug_text = UnderlinedSimpleText(
            text=text,
            pos=(0, 0),
            anchor=LEFT,
            color=WHITESMOKE,
            underline_color=MultiGradient(*RAINBOW))
        self.bug_reports_checkbox = CheckBox(text=text,
                                             pos=(size[0] // 2, size[1] - 90),
                                             anchor=BOTTOM,
                                             bg_color=DARK_GREY,
                                             shape=RoundedRect((1120, 50), rounding=100))
        # this is just a trick to replace the SimpleText widget of the CheckBox with the UnderlinedSimpleText
        bug_text.pos = self.bug_reports_checkbox.text_widget.pos
        self.bug_reports_checkbox.children.remove(self.bug_reports_checkbox.text_widget)
        self.bug_reports_checkbox.text_widget = self.bug_reports_checkbox.add_child(bug_text)

        self.kalach_text = SimpleText(text="Get more Kalachnikovs to unlock more!",
                                      pos=(size[0] // 2, size[1] // 2 + 200),
                                      color=WHITESMOKE,
                                      anchor=BOTTOM)

        # Buttons
        menu_button = MenuButton(app, (size[0] - 135, 250))
        key_bindings = Button(text="Key Bindings",
                              function=lambda: app.set_screen(KEY_BIND),
                              shape=RoundedRect((250, 50), 100),
                              color=Monokai.PINK,
                              bg_color=DARK_GREY,
                              pos=menu_button.absolute_rect.midleft + Pos(-10, 0),
                              anchor=RIGHT)

        clear_config = Button(text="Clear all configuration and all stats",
                              function=self.config_clearer,
                              shape=RoundedRect((600, 50), 100),
                              color=WHITESMOKE,
                              bg_color=LLAMA + (100,),
                              pos=(size[0] // 2, size[1] - 20),
                              anchor=BOTTOM)

        widgets = [
            Title("Settings", size),
            self.player_selector,
            self.bug_reports_checkbox,
            self.kalach_text,
            menu_button,
            key_bindings,
            clear_config
        ]

        self.bug_reports_checkbox.checked = CONFIG.send_log
        self.player_selector.option_index = CONFIG.player
        self.img_preview = pygame.image.load(os.path.join(PLAYER_FOLDER,
                                                          PLAYERS[self.player_selector.option_index][0])).convert()
        self.img_preview.set_colorkey((255, 0, 255))
        for _ in range(3):
            self.img_preview = pygame.transform.scale2x(self.img_preview)

        super().__init__(app, widgets, (20, 10, 0))

    def internal_logic(self):
        if CONFIG.send_log != self.bug_reports_checkbox.checked:
            CONFIG.send_log = self.bug_reports_checkbox.checked

    def player_setter(self, player):
        LOGGER.info(f"Setting player to {player}")
        CONFIG.player = get_index_from_name(PLAYERS, player)
        self.img_preview = pygame.image.load(os.path.join(PLAYER_FOLDER,
                                                          PLAYERS[self.player_selector.option_index][0])).convert()
        self.img_preview.set_colorkey((255, 0, 255))
        for _ in range(3):
            self.img_preview = pygame.transform.scale2x(self.img_preview)

    def config_clearer(self):
        CONFIG.__reset__()
        self.app.set_screen(USER_AGREE)

    def render(self, display):
        super().render(display)

        rect = self.img_preview.get_rect()
        rect.midbottom = Pos(self.player_selector.absolute_rect.midtop) - (0, 50)
        display.blit(self.img_preview, rect)
