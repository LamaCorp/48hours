#!/usr/bin/env python
import pygame
from graphalama.app import App

from constants import MENU, PICKER, SETTINGS, STATS
from menu import MenuScreen
from picker import PickerScreen
from settings import SettingsScreen
from statistics import StatisticsScreen
from config import CONFIG

pygame.init()


def main():
    App({
        MENU: MenuScreen,
        PICKER: PickerScreen,
        SETTINGS: SettingsScreen,
        STATS: StatisticsScreen,
    }, MENU).run()


if __name__ == "__main__":
    # ensure it saves
    with CONFIG:
        main()
