import os
from typing import List
import pygame
import logging

from graphalama.app import Screen
from graphalama.buttons import Button, CarouselSwitch
from graphalama.constants import LLAMA, GREY
from graphalama.core import Widget

from constants import PLAYER_FOLDER
from config import CONFIG

LOGGER = logging.getLogger(__name__)


class IdleScreen(Screen):
    FPS = 60

    def __init__(self, app, widgets=(), bg_color=None):
        LOGGER.info("Starting an IdleScreen")
        if bg_color is None:
            bg_color = (0, 0, 0)
        self.lama_logo = pygame.image.load(os.path.join(PLAYER_FOLDER, "lama_normal.png")).convert()
        self.lama_logo.set_colorkey((255, 0, 255))
        for _ in range(3):
            self.lama_logo = pygame.transform.scale2x(self.lama_logo)
        self.lama_logo_left = pygame.transform.flip(self.lama_logo, True, False)
        self.focused_button_index = -1
        for i in range(len(widgets)):
            if isinstance(widgets[i], Button):
                self.focused_button_index = i
                break
        super().__init__(app=app, widgets=widgets, bg_color=bg_color)
    
    def draw_background(self, display):
        super().draw_background(display)
        self.draw_lamas(display)

    def draw_lamas(self, display):
        rect = self.lama_logo.get_rect()
        size = self.app.display.get_size()
        rect.center = (size[0] // 5, size[1] // 2)
        display.blit(self.lama_logo, rect)
        rect.center = (size[0] * 4/5, size[1] // 2)
        display.blit(self.lama_logo_left, rect)

    def get_next_button(self):
        for i in range(self.focused_button_index + 1, len(self.widgets)):
            if isinstance(self.widgets[i], Button) and not isinstance(self.widgets[i], CarouselSwitch):
                return i
        for i in range(self.focused_button_index + 1):
            if isinstance(self.widgets[i], Button) and not isinstance(self.widgets[i], CarouselSwitch):
                return i
        return -1

    def get_previous_button(self):
        for i in range(self.focused_button_index - 1, -1, -1):
            if isinstance(self.widgets[i], Button) and not isinstance(self.widgets[i], CarouselSwitch):
                return i
        for i in range(len(self.widgets) - 1, self.focused_button_index - 1, -1):
            if isinstance(self.widgets[i], Button) and not isinstance(self.widgets[i], CarouselSwitch):
                return i
        return -1

    def carousel_exists(self):
        for widget in self.widgets:
            if isinstance(widget, CarouselSwitch):
                return True
        return False

    def get_first_carousel(self):
        for widget in self.widgets:
            if isinstance(widget, CarouselSwitch):
                return widget

    @staticmethod
    def focus_render(widgets: List[Widget], i):
        if i == -1:
            LOGGER.warning(f"We somehow lost track of next button :/")
            return
        LOGGER.info(f"Focusing widget {widgets[i]}")
        widgets[i].shape.set_border_and_fix_center(2)
        widgets[i].border_color = LLAMA

    @staticmethod
    def unfocus_render(widgets: List[Widget], i):
        if i == -1:
            LOGGER.warning("We somehow lost track of the previous button :/")
            return
        LOGGER.info(f"Un-focusing widget {widgets[i]}")
        widgets[i].border_color = GREY
        widgets[i].shape.set_border_and_fix_center(0)

    def update(self, event):
        if self.focused_button_index == -1:
            return

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                LOGGER.info(f"Keyboard activated focused button")
                self.widgets[self.focused_button_index].function()
            elif event.key == pygame.K_DOWN or event.key == pygame.K_TAB:
                LOGGER.info(f"Trying to focus next button")
                self.unfocus_render(self.widgets, self.focused_button_index)
                self.focused_button_index = self.get_next_button()
                LOGGER.info(f"Next button is the one that now will be focused")
                self.focus_render(self.widgets, self.focused_button_index)
            elif event.key == pygame.K_UP or \
                    (((pygame.key.get_mods() & pygame.KMOD_LSHIFT) or
                      (pygame.key.get_mods() & pygame.KMOD_RSHIFT))
                     and event.key == pygame.K_TAB):
                LOGGER.info(f"Trying to focus previous button")
                self.unfocus_render(self.widgets, self.focused_button_index)
                self.focused_button_index = self.get_previous_button()
                LOGGER.info(f"Previous button is the one that now will be focused")
                self.focus_render(self.widgets, self.focused_button_index)
            if self.carousel_exists():  # TODO: Possible amelioration: handle the case where there are several carousels
                carousel = self.get_first_carousel()
                if event.key == pygame.K_LEFT:
                    LOGGER.info(f"Carousel: {carousel}")
                    carousel.option_index -= 1
                    LOGGER.info(f"Going to the left to option #{carousel.option_index}")
                elif event.key == pygame.K_RIGHT:
                    LOGGER.info(f"Carousel: {carousel}")
                    carousel.option_index += 1
                    LOGGER.info(f"Going to the right to option #{carousel.option_index}")

        super().update(event)
