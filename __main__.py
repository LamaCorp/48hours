#!/usr/bin/env python
from log import init_logger, log_sysinfo; init_logger()
import pygame
import logging

from graphalama.app import App

from screens.menu import MenuScreen
from screens.picker import PickerScreen
from screens.settings import SettingsScreen
from screens.statistics import StatisticsScreen
from screens.key_bindings import KeyBindingsScreen
from screens.user_agreement import UserAgreementScreen
from constants import VERSION, MENU, PICKER, SETTINGS, STATS, KEY_BIND, USER_AGREE
from config import CONFIG

# This is to trigger the initialization of sentry_sdk
CONFIG.send_log = CONFIG.send_log
LOGGER = logging.getLogger(__name__)

pygame.init()

__version__ = VERSION


def main():
    LOGGER.info("Starting the game.")
    first_time_config = CONFIG.first_time_launch
    start_screen = USER_AGREE if first_time_config else MENU
    App({
        MENU: MenuScreen,
        PICKER: PickerScreen,
        SETTINGS: SettingsScreen,
        STATS: StatisticsScreen,
        KEY_BIND: KeyBindingsScreen,
        USER_AGREE: UserAgreementScreen,
    }, start_screen).run()
    LOGGER.info("Exiting the game.")


if __name__ == "__main__":
    log_sysinfo()
    # ensure it saves
    with CONFIG:
        main()
