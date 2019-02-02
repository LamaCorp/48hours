#!/usr/bin/env python
from graphalama.app import App
import pygame

from game import GameScreen
from menu import MenuScreen
from picker import PickerScreen
from constants import MENU, GAME, SETTINGS, PICKER
pygame.init()


def main():
    App({
        MENU: MenuScreen,
        PICKER: PickerScreen,
        # TODO: settings
    }, MENU).run()


if __name__ == "__main__":
    main()