from graphalama.app import Screen

from graphalama.buttons import CarouselSwitch
from graphalama.shapes import RoundedRect
from graphalama.constants import BOTTOM, WHITESMOKE

from widgets import MenuButton, SettingsButton, PlayButton
from constants import LIGHT_DARK
from config import get_available_levels


class PickerScreen(Screen):
    FPS = 60

    def __init__(self, app):
        self.level = get_available_levels[0]
        size = app.display.get_size()
        self.play_button = PlayButton(app, self.level, (size[0] // 2, size[1] // 2 + 200))
        widgets = [
            MenuButton(app, (size[0] - 365, 100)),
            SettingsButton(app, (size[0] - 65, 100)),
            CarouselSwitch(options=get_available_levels,
                           on_choice=self.level_setter,
                           pos=(size[0] // 2, size[1] // 2 - 200),
                           shape=RoundedRect((300, 50)),
                           color=WHITESMOKE,
                           bg_color=LIGHT_DARK,
                           arrow_color=WHITESMOKE,
                           anchor=BOTTOM),
            self.play_button,
        ]

        super().__init__(app, widgets, None)  # TODO: add background

    def level_setter(self, level):
        self.level = level
        # FIXME: doesn't change the level at all
