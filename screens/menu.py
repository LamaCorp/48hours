from screens.idle_screen import IdleScreen
from screens.widgets import Title, PickerButton, SettingsButton, QuitButton, StatisticsButton


class MenuScreen(IdleScreen):
    def __init__(self, app):
        size = app.display.get_size()
        def pos(n):
            return (size[0] // 2, size[1] // 2 + 75 * (n - 1.5))
        widgets = [
            Title("Llama destroys the world", size),
            PickerButton(app, pos(0)),
            StatisticsButton(app, pos(1)),
            SettingsButton(app, pos(2)),
            QuitButton(app, pos(3)),
        ]

        super().__init__(app, widgets, (20, 10, 0))
