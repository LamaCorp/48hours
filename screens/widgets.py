from functools import lru_cache
from time import time

import pygame
from graphalama.buttons import CarouselSwitch
from graphalama.colors import Gradient, MultiGradient, mix
from graphalama.constants import (CENTER, NICE_BLUE, PURPLE, GREEN,
                                  Monokai, YELLOW, RED, TOP, WHITESMOKE, RAINBOW, LEFT, RIGHT, TRANSPARENT, LLAMA,
                                  TOPRIGHT, TOPLEFT)
from graphalama.core import Widget
from graphalama.font import default_font
from graphalama.maths import Pos
from graphalama.shadow import NoShadow
from graphalama.shapes import RoundedRect, Rectangle
from graphalama.widgets import SimpleText, Button

from constants import MENU, SETTINGS, PICKER, STATS, LIGHT_DARK, DARK, GREY


def Title(text, screen_size, anchor=TOP, font_size=150):
    return SimpleText(text=text,
                      pos=(screen_size[0] / 2, 50),
                      shape=Rectangle((screen_size[0] + 2, 200), border=1),
                      color=MultiGradient(*RAINBOW),
                      # bg_color=DARK + (172,),
                      bg_color=(30,) * 3,
                      border_color=MultiGradient(*RAINBOW),
                      font=default_font(font_size),
                      anchor=anchor)


def SettingsButton(app, pos=None, anchor=CENTER):
    return Button(text="Settings",
                  function=lambda: app.set_screen(SETTINGS),
                  shape=RoundedRect((200, 50), 100),
                  color=RED,
                  bg_color=GREY,
                  pos=pos,
                  anchor=anchor)


def StatisticsButton(app, pos=None, anchor=CENTER):
    return Button(text="Statistics",
                  function=lambda: app.set_screen(STATS),
                  shape=RoundedRect((200, 50), 100),
                  color=NICE_BLUE,
                  bg_color=GREY,
                  pos=pos,
                  anchor=anchor)


def PickerButton(app, pos=None, anchor=CENTER):
    return Button(text="Play",
                  function=lambda: app.set_screen(PICKER),
                  shape=RoundedRect((300, 50), 100),
                  color=WHITESMOKE,
                  bg_color=Gradient(NICE_BLUE, PURPLE),
                  pos=pos,
                  anchor=anchor)


def PlayButton(app, pos=None, anchor=CENTER):
    from screens.game import GameScreen
    from level import Level
    from config import CONFIG

    button = PickerButton(app, pos, anchor)
    button.function = lambda: app.set_temp_screen(lambda app: GameScreen(app, Level.load_num(CONFIG.level))),
    return button


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
                  shape=RoundedRect((300, 50), 100),
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


class Segment(Widget):

    def __init__(self, a, b, color=None):
        size = (abs(a[0] - b[0]) + 1,
                abs(a[1] - b[1]) + 1)
        topleft = (min(a[0], b[0]),
                   min(a[1], b[1]))

        a, b = sorted((a, b))
        if a == topleft:
            if a[1] == b[1]:
                self.case = "-"  # horizontal
            elif a[0] == b[0]:
                self.case = "|"  # veritcal
            else:
                self.case = "\\"  # diagonal segment \
        else:
            self.case = "/"  # diagonal /

        super().__init__(pos=topleft,
                         shape=Rectangle(size, border=0, padding=0),
                         color=color,
                         bg_color=TRANSPARENT,
                         shadow=NoShadow(),
                         anchor=TOPLEFT)

    def draw_content(self, content_surf):
        w, h = content_surf.get_size()
        if self.case == "-":
            pygame.draw.line(content_surf, self.color.color, (0, 0), (w, 0))
        elif self.case == "|":
            pygame.draw.line(content_surf, self.color.color, (0, 0), (0, h))
        elif self.case == "\\":
            pygame.draw.line(content_surf, self.color.color, (0, 0), (w, h))
        else:
            pygame.draw.line(content_surf, self.color.color, (0, h), (w, 0))


class SurfaceButton(Button):
    """A button displaying an image from a surface"""

    def __init__(self, surf, function, resize=False, resize_smooth=False,
                 pos=None, shape=None,
                 color=None, bg_color=None, shadow=None, anchor=None):
        self.resize_surf = resize
        self.resize_smooth = resize_smooth
        self.surf = surf
        if bg_color is None:
            bg_color = TRANSPARENT
        super().__init__("", function, pos=pos, shape=shape, color=color, bg_color=bg_color, shadow=shadow,
                         anchor=anchor)

    def draw_content(self, content_surf):
        if self.resize_surf:
            if self.resize_smooth:
                surf = pygame.transform.smoothscale(self.surf, content_surf.get_size())
            else:
                surf = pygame.transform.scale(self.surf, content_surf.get_size())
        else:
            surf = self.surf

        content_surf.blit(surf, (0, 0))
