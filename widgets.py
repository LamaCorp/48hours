from functools import lru_cache
from time import time

import pygame
from graphalama.buttons import CarouselSwitch
from graphalama.colors import Gradient, MultiGradient
from graphalama.constants import (CENTER, NICE_BLUE, PURPLE, GREEN,
                                  Monokai, YELLOW, RED, TOP, WHITESMOKE, RAINBOW, LEFT, RIGHT, TRANSPARENT, LLAMA,
                                  TOPRIGHT)
from graphalama.font import default_font
from graphalama.maths import Pos
from graphalama.shapes import RoundedRect, Rectangle
from graphalama.widgets import SimpleText, Button

from constants import MENU, SETTINGS, PICKER, STATS, LIGHT_DARK, DARK


def Title(text, screen_size, anchor=TOP):
    return SimpleText(text=text,
                      pos=(screen_size[0] / 2, 50),
                      shape=Rectangle((screen_size[0] + 2, 200), border=1),
                      color=MultiGradient(*RAINBOW),
                      bg_color=DARK + (172,),
                      border_color=MultiGradient(*RAINBOW),
                      font=default_font(150),
                      anchor=anchor)


def SettingsButton(app, pos=None, anchor=CENTER):
    return Button(text="Settings",
                  function=lambda: app.set_screen(SETTINGS),
                  shape=RoundedRect((200, 50), 100),
                  color=Monokai.PINK,
                  bg_color=(200, 200, 200, 72),
                  pos=pos,
                  anchor=anchor)


def StatisticsButton(app, pos=None, anchor=CENTER):
    return Button(text="Statistics",
                  function=lambda: app.set_screen(STATS),
                  shape=RoundedRect((200, 50), 100),
                  color=Monokai.PURPLE,
                  bg_color=(200, 200, 200, 72),
                  pos=pos,
                  anchor=anchor)


def PickerButton(app, pos=None, anchor=CENTER):
    return Button(text="Play",
                  function=lambda: app.set_screen(PICKER),
                  shape=RoundedRect((200, 50), 100),
                  color=WHITESMOKE,
                  bg_color=Gradient(NICE_BLUE, PURPLE),
                  pos=pos,
                  anchor=anchor)


def PlayButton(app, pos=None, anchor=CENTER):
    from game import GameScreen
    from level import Level
    from config import CONFIG
    return Button(text="Play",
                  function=lambda: app.set_temp_screen(lambda app: GameScreen(app, Level.load_num(CONFIG.level))),
                  pos=pos,
                  shape=RoundedRect((200, 50), 100),
                  color=WHITESMOKE,
                  bg_color=Gradient(NICE_BLUE, PURPLE),
                  anchor=anchor)


def ResumeButton(function, pos=None, anchor=CENTER):
    return Button(text="Resume",
                  function=function,
                  pos=pos,
                  shape=RoundedRect((200, 50), 100),
                  color=WHITESMOKE,
                  bg_color=Gradient(NICE_BLUE, PURPLE),
                  anchor=anchor)


def MenuButton(app, pos=None, anchor=CENTER):
    return Button(text="Menu",
                  function=lambda: app.set_screen(MENU),
                  shape=RoundedRect((200, 50), 100),
                  color=WHITESMOKE,
                  bg_color=Gradient(GREEN, Monokai.GREEN),
                  pos=pos,
                  anchor=anchor)


def QuitButton(app, pos=None, anchor=CENTER):
    """A button that exits the app."""
    return Button(text="Quit",
                  function=app.quit,
                  pos=pos,
                  shape=RoundedRect((200, 50), 100),
                  color=WHITESMOKE,
                  bg_color=Gradient(YELLOW, RED),
                  anchor=anchor)


def SettingsCarousel(options, func, pos):
    return CarouselSwitch(options, func, pos, RoundedRect((300, 50)),
                          color=WHITESMOKE,
                          bg_color=LIGHT_DARK,
                          arrow_color=WHITESMOKE,
                          anchor=LEFT)


def SettingsLabel(name, pos):
    return SimpleText(name + "  ", pos, color=WHITESMOKE, anchor=RIGHT)


def PauseButton(function, pos=None):
    """A button that pauses the game by calling function """
    return Button(text="||",
                  function=function,
                  pos=pos,
                  color=LLAMA,
                  bg_color=TRANSPARENT,
                  anchor=TOPRIGHT)


class CountDown(SimpleText):
    """Big timer before the end of the game."""

    def __init__(self, countdown, pos=None, color=WHITESMOKE, critical_color=RED,
                 good_color=Monokai.GREEN, font=None, anchor=None):
        """
        Timer that goes to 0 after countdown seconds.
        """

        font = font if font is not None else default_font(150)

        self.timer_at_pause = None
        self.normal_color = color
        self.critical_color = critical_color
        self.good_color = good_color
        self.countdown = countdown
        self.start_time = time()
        self.last_added = time()

        size = font.size("9:99:999")
        super().__init__("", pos, size, color=color, font=font, anchor=anchor, text_anchor=TOP | LEFT)
        self.transparency = 128

    @property
    def remaining_time(self):
        """Time left before the countdown is over."""
        remaining = self.start_time + self.countdown - time()
        if remaining < 0:
            return 0
        return remaining

    def pre_render_update(self):
        if self.timer_at_pause:
            return

        rem = self.remaining_time
        milis = int(rem % 1 * 1000)
        sec = int(rem % 60)
        minu = int(rem // 60)

        s = '{}:{:02}:{:>03}'.format(minu, sec, milis)
        self.text = s

        if self.last_added - self.remaining_time < 0.5:
            self.color = self.good_color
        elif milis < 200:
            self.color = self.critical_color
        elif minu == 0 and sec < 30:
            self.color = self.critical_color
        else:
            self.color = self.normal_color

    @property
    def over(self):
        """Countdown is over."""
        return self.remaining_time == 0

    def pause(self):
        self.timer_at_pause = self.remaining_time

    def resume(self):
        self.start_time = time() - (self.countdown - self.timer_at_pause)
        self.timer_at_pause = None

    def add(self, sec):
        self.countdown += sec
        self.last_added = self.remaining_time

    def draw_content(self, content_surf: pygame.Surface):
        pos = Pos(0, 0)
        for c in self.text:
            surf = self.render_char(c, self.color.color)
            content_surf.blit(surf, pos)
            pos += surf.get_width(), 0

        content_surf.set_alpha(self.transparency)
        content_surf.set_colorkey((0,0,0))

    @lru_cache(maxsize=11*3)  # three colors * (10 digits + colon)
    def render_char(self, char, color):
        return self.font.render(char, False, color, )

    @property
    def content_image(self):
        if not self._content:
            # we override this because we don't want per pixel alpha on the big text, otherwise
            # it takes 20% of the game time to blit it

            # create a normal surface
            self._content = pygame.Surface(self.content_rect.size)
            self.draw_content(self._content)
        return self._content
