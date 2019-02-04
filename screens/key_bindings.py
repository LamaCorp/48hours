from enum import Enum, auto

import pygame
from graphalama.buttons import Button, CarouselSwitch, CheckBox, ImageButton
from graphalama.colors import ImageBrush
from graphalama.core import Widget
from graphalama.shadow import NoShadow
from graphalama.shapes import RoundedRect, Rectangle
from graphalama.text import SimpleText
from graphalama.constants import BOTTOM, WHITESMOKE, Monokai, CENTER, LLAMA, LEFT, RIGHT

from physics import Pos
from screens.widgets import Title, SurfaceButton
from constants import LIGHT_DARK, SETTINGS
from config import CONFIG
from screens.idle_screen import IdleScreen
from screens import keys


class Binding(Enum):
    LEFT = 'Left'
    RIGHT = 'Right'
    JUMP = 'Jump'
    RUN = 'Run'

class KeyBindingsScreen(IdleScreen):
    def __init__(self, app):
        self.binding_setting = None
        self.binding_widgets = {}

        size = app.display.get_size()
        def bind(binding, n):
            y = size[1] // 2 + 100 * (n - 1.5)
            x = size[0] // 2 - 150

            text = SimpleText(text=binding.value,
                                 pos=(x, y),
                                 color=WHITESMOKE,
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

        widgets = [
            Title("Key bindings", size),
            Widget((size[0] // 2, size[1] // 2),
                   shape=RoundedRect((400, 400), rounding=20, percent=False),
                   bg_color=(100, 100, 100, 180),
                   anchor=CENTER),
            *bind(Binding.LEFT, 0),
            *bind(Binding.RIGHT, 1),
            *bind(Binding.JUMP, 2),
            *bind(Binding.RUN, 3),
            Button(text="Back",
                   function=lambda: app.set_screen(SETTINGS),
                   shape=RoundedRect((200, 50), 100),
                   color=Monokai.PINK,
                   bg_color=(200, 200, 200, 72),
                   pos=(size[0] // 2, size[1] - 200),
                   anchor=CENTER),
        ]

        super().__init__(app, widgets, (20, 10, 0))

    def update(self, event):
        if self.binding_setting is not None:
            if event.type == pygame.KEYDOWN:
                self.set_binding(self.binding_setting, event.key)

                # update the inage
                wid = self.binding_widgets[self.binding_setting]
                img = keys.name_to_img(self.get_binding_key(self.binding_setting))
                img = pygame.transform.scale(img, Pos(img.get_size()) * 4)
                wid.surf = img
                wid.size = img.get_size()
                wid.invalidate_content()

                self.binding_setting = None
                return True
        super().update(event)


    def start_set_func(self, binding):
        def inner():
            print("set", binding)
            self.binding_setting = binding
        return inner

    def get_binding_key(self, binding: Binding):
        key_code = getattr(CONFIG.bindings, binding.value.lower())
        name = pygame.key.name(key_code)
        return name

    def set_binding(self, binding: Binding, keycode: int):
        setattr(CONFIG.bindings, binding.value.lower(), keycode)

