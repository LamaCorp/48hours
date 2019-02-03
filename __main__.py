#!/usr/bin/env python
import pygame
from graphalama.app import App

from constants import MENU, PICKER, SETTINGS
from menu import MenuScreen
from picker import PickerScreen
from settings import SettingsScreen

pygame.init()


def main():
    App({
        MENU: MenuScreen,
        PICKER: PickerScreen,
        SETTINGS: SettingsScreen,
    }, MENU).run()


if __name__ == "__main__":
    main()
