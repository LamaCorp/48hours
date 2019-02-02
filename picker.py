from graphalama.app import Screen

from graphalama.buttons import CarouselSwitch

from constants import GAME, SETTINGS, MENU
from widgets import MenuButton, SettingsButton, PlayButton

from config import get_available_levels


class PickerScreen(Screen):
    FPS = 60

    def __init__(self, app):
        self.level = get_available_levels[0]
        size = app.display.get_size()
        widgets = [
            MenuButton(app, (size[0] - 200, 100)),
            SettingsButton(app, (size[0] - 65, 100)),
            PlayButton(app, self.level, (size[0] // 2, size[1] // 2)),
        ]

        super().__init__(app, widgets, None) # TODO: add background