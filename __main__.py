#!/usr/bin/env python
import pygame
from graphalama.app import App

from constants import MENU, PICKER, SETTINGS, STATS, KEY_BIND
from screens.menu import MenuScreen
from screens.picker import PickerScreen
from screens.settings import SettingsScreen
from screens.statistics import StatisticsScreen
from screens.key_bindings import KeyBindingsScreen
from config import CONFIG

pygame.init()

__version__ = "1.0"


def main():
    App({
        MENU: MenuScreen,
        PICKER: PickerScreen,
        SETTINGS: SettingsScreen,
        STATS: StatisticsScreen,
        KEY_BIND: KeyBindingsScreen,
    }, MENU).run()


if __name__ == "__main__":
    # ensure it saves
    with CONFIG:
        main()
