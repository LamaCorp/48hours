#!/usr/bin/env python
import pygame
from graphalama.app import App

from constants import MENU, PICKER
from menu import MenuScreen
from picker import PickerScreen

pygame.init()


def main():
    App({
        MENU: MenuScreen,
        PICKER: PickerScreen,
        # TODO: settings
    }, MENU).run()


if __name__ == "__main__":
    main()
