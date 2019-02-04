from graphalama.buttons import Button, CarouselSwitch, CheckBox
from graphalama.core import Widget
from graphalama.shapes import RoundedRect
from graphalama.text import SimpleText
from graphalama.constants import BOTTOM, WHITESMOKE, Monokai, CENTER, LEFT, LLAMA

from widgets import MenuButton, Title
from constants import LIGHT_DARK, PLAYER_FOLDER, SETTINGS
from config import CONFIG, KEYS_DICTS
from idle_screen import IdleScreen


class KeyBindingsScreen(IdleScreen):
    def __init__(self, app):
        size = app.display.get_size()

        def pos(n, block):
            return (size[0] // 2 + (n - 1.5) * 300,
                   size[1] // 2 + (block - 0.3) * 150)



        def check(text, n, block):
            return CheckBox(text=text,
                            pos=pos(n, block),
                            color=WHITESMOKE,
                            anchor=CENTER)

        self.selector_move = CarouselSwitch(options=list(KEYS_DICTS["MOVE"]),
                                            on_choice=KeyBindingsScreen.bindings_setter,
                                            pos=(size[0] // 2, size[1] // 2 - 150),
                                            shape=RoundedRect((300, 75)),
                                            color=WHITESMOKE,
                                            bg_color=LIGHT_DARK,
                                            arrow_color=WHITESMOKE,
                                            anchor=BOTTOM)
        self.run_lshift_checkbox = check("Left Shift", 0, 0)
        self.run_rshift_checkbox = check('Right Shift', 1, 0)
        self.run_lctrl_checkbox = check('Left Ctrl', 2, 0)
        self.run_rctrl_checkbox = check('Right Ctrl', 3, 0)

        self.jump_space_checkbox = check('Space Bar', 0, 1)
        self.jump_w_checkbox = check('W', 1, 1)
        self.jump_z_checkbox = check('Z', 2, 1)
        self.jump_uparrow_checkbox = check('Up arrow', 3, 1)

        widgets = [
            Title("Key bindings", size),
            Widget((size[0] // 2, size[1] // 2),
                   shape=RoundedRect((1200, 400), rounding=20, percent=False),
                   bg_color=(100, 100, 100, 180),
                   anchor=CENTER),
            SimpleText(text="Moving around",
                       pos=(size[0] // 2, size[1] // 2 - 255),
                       color=LLAMA,
                       anchor=CENTER),
            self.selector_move,

            SimpleText(text="Running",
                       pos=(size[0] // 2, size[1] // 2 - 100),
                       color=LLAMA,
                       anchor=CENTER),
            self.run_lshift_checkbox,
            self.run_rshift_checkbox,
            self.run_lctrl_checkbox,
            self.run_rctrl_checkbox,

            SimpleText(text="Might as well jump!",
                       pos=(size[0] // 2, size[1] // 2 + 50),
                       color=LLAMA,
                       anchor=CENTER),
            self.jump_space_checkbox,
            self.jump_w_checkbox,
            self.jump_z_checkbox,
            self.jump_uparrow_checkbox,

            Button(text="Back",
                   function=lambda: app.set_screen(SETTINGS),
                   shape=RoundedRect((200, 50), 100),
                   color=Monokai.PINK,
                   bg_color=(200, 200, 200, 72),
                   pos=(size[0] // 2, size[1] - 200),
                   anchor=CENTER),
        ]

        for w in widgets:
            if isinstance(w, CheckBox):
                if w.text_widget.text in KEYS_DICTS["RUN"] and \
                        KEYS_DICTS["RUN"][w.text_widget.text] in CONFIG.key_bindings["RUN"]:
                    w.checked = True
                elif w.text_widget.text in KEYS_DICTS["JUMP"] and \
                        KEYS_DICTS["JUMP"][w.text_widget.text] in CONFIG.key_bindings["JUMP"]:
                    w.checked = True

        super().__init__(app, widgets, (20, 10, 0))

    def internal_logic(self):
        CONFIG.key_bindings["RUN"] = []
        CONFIG.key_bindings["JUMP"] = []
        for w in self.widgets:
            if isinstance(w, CheckBox):
                if w.text_widget.text in KEYS_DICTS["RUN"]:
                    CONFIG.key_bindings["RUN"].append(KEYS_DICTS["RUN"][w.text_widget.text])
                elif w.text_widget.text in KEYS_DICTS["JUMP"]:
                    CONFIG.key_bindings["JUMP"].append(KEYS_DICTS["JUMP"][w.text_widget.text])

    @classmethod
    def bindings_setter(cls, binding):
        CONFIG.key_bindings["LEFT"] = []
        CONFIG.key_bindings["RIGHT"] = []
        CONFIG.key_bindings["LEFT"].append(KEYS_DICTS["MOVE"][binding][0])
        CONFIG.key_bindings["RIGHT"].append(KEYS_DICTS["MOVE"][binding][1])
