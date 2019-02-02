from graphalama.app import Screen

from constants import SETTINGS, PICKER
from widgets import Title, PickerButton, SettingsButton, QuitButton

class MenuScreen(Screen):
    FPS = 30

    def __init__(self, app):
        size = app.display.get_size()
        widgets = [
            Title("Llama destroys the world", size),
            PickerButton(app, (size[0] // 2, size[1] // 2 - 65)),
            SettingsButton(app, (size[0] // 2, size[1] // 2)),
            QuitButton(app, (size[0] // 2, size[1] // 2 + 65)),
        ]

        super().__init__(app, widgets, None) # TODO: add background image or animation or video