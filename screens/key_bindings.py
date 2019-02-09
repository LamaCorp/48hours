from enum import Enum
import pygame
import logging

from graphalama.buttons import Button
from graphalama.colors import ImageBrush
from graphalama.core import Widget
from graphalama.shadow import NoShadow
from graphalama.shapes import RoundedRect, Rectangle
from graphalama.text import SimpleText
from graphalama.constants import BOTTOM, CENTER, LLAMA, LEFT, RIGHT

from physics import Pos
from screens.widgets import Title, SurfaceButton
from constants import SETTINGS, DARK
from config import CONFIG
from screens.idle_screen import IdleScreen
from screens import keys

LOGGER = logging.getLogger(__name__)


class Binding(Enum):
    LEFT = 'Left'
    RIGHT = 'Right'
    JUMP = 'Jump'
    RUN = 'Run'


class KeyBindingsScreen(IdleScreen):
    def __init__(self, app):
        LOGGER.info("Starting a KeyBindingsScreen")
        self.binding_setting = None
        self.binding_widgets = {}

        size = app.display.get_size()

        def bind(binding, n):
            y = size[1] // 2 + 90 * (n - 1.5)
            x = size[0] // 2 - 150

            text = SimpleText(text=binding.value,
                              pos=(x, y),
                              color=LLAMA,
                              anchor=LEFT)

            img = keys.name_to_img(self.get_binding_key(binding))
            img = pygame.transform.scale(img, Pos(img.get_size()) * 4)

            key = SurfaceButton(surf=img,
                                function=self.start_set_func(binding),
                                pos=(x + 300, y),
                                color=ImageBrush(img),
                                shadow=NoShadow(),
                                shape=Rectangle(img.get_size(), padding=0),
                                anchor=RIGHT)
            self.binding_widgets[binding] = key

            return text, key

        self.hint_label = SimpleText(text="Press anything to set the ... binding",
                                     pos=(size[0] // 2, size[1] - 100),
                                     anchor=BOTTOM,
                                     color=LLAMA)
        self.hint_label.visible = False

        widgets = [
            Title("Key bindings", size),
            Widget((size[0] // 2, size[1] // 2),
                   shape=RoundedRect((400, 450), rounding=20, percent=False),
                   bg_color=DARK,
                   anchor=CENTER),
            *bind(Binding.LEFT, 0),
            *bind(Binding.RIGHT, 1),
            *bind(Binding.JUMP, 2),
            *bind(Binding.RUN, 3),
            Button(text="Back",
                   function=lambda: app.set_screen(SETTINGS),
                   shape=RoundedRect((200, 50), 100, border=2),
                   color=LLAMA,
                   bg_color=DARK,
                   border_color=LLAMA,
                   pos=(size[0] // 2, size[1] // 2 + 225),
                   anchor=CENTER),
            self.hint_label,
        ]

        super().__init__(app, widgets, (20, 10, 0))

    def update(self, event):
        if self.binding_setting is not None:
            if event.type == pygame.KEYDOWN:
                LOGGER.info(f"Setting a binding. Key code: {event.key}")
                self.set_binding(self.binding_setting, event.key)

                # update the image
                wid = self.binding_widgets[self.binding_setting]
                img = keys.name_to_img(self.get_binding_key(self.binding_setting))
                img = pygame.transform.scale(img, Pos(img.get_size()) * 4)
                wid.surf = img
                wid.size = img.get_size()
                wid.invalidate_content()

                self.hint_label.visible = False
                self.binding_setting = None
                return True
        super().update(event)

    def start_set_func(self, binding):
        def inner():
            self.binding_setting = binding
            self.hint_label.text = "Press anything to set the {} binding.".format(binding.value.lower())
            self.hint_label.visible = True
        return inner

    @staticmethod
    def get_binding_key(binding: Binding):
        key_code = getattr(CONFIG.bindings, binding.value.lower())
        name = pygame.key.name(key_code)
        return name

    @staticmethod
    def set_binding(binding: Binding, keycode: int):
        setattr(CONFIG.bindings, binding.value.lower(), keycode)
