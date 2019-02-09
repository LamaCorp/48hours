import logging

from graphalama.colors import MultiGradient
from graphalama.core import Widget
from graphalama.buttons import Button
from graphalama.font import default_font
from graphalama.shadow import Shadow
from graphalama.shapes import RoundedRect
from graphalama.constants import CENTER, WHITESMOKE, RAINBOW, PURPLE, RED, YELLOW, GREEN, BLUE, ORANGE, PINK, \
    BOTTOM
from graphalama.text import SimpleText

from constants import MENU, DARK_GREY
from physics import Pos
from screens.idle_screen import IdleScreen
from config import CONFIG

LOGGER = logging.getLogger(__name__)


class UserAgreementScreen(IdleScreen):
    def __init__(self, app):
        LOGGER.info("Starting a UserAgreementScreen")
        size = app.display.get_size()

        back_box = Widget(pos=(size[0] // 2, size[1] // 2),
                          shape=RoundedRect((700, 400), border=2, rounding=35, percent=False),
                          border_color=MultiGradient(*RAINBOW),
                          bg_color=DARK_GREY,
                          anchor=CENTER)

        text1 = SimpleText(text="To send anonymous information",
                           pos=Pos(back_box.absolute_rect.midtop) + (0, 100),
                           color=WHITESMOKE,
                           anchor=CENTER)
        text2 = SimpleText(text="about your gameplay",
                           pos=Pos(text1.absolute_rect.midtop) + (0, 75),
                           color=WHITESMOKE,
                           anchor=CENTER)
        text3 = SimpleText(text="in case the game crashes",
                           pos=Pos(text2.absolute_rect.midtop) + (0, 75),
                           color=WHITESMOKE,
                           anchor=CENTER)
        text4 = SimpleText(text="so we can improve the game?",
                           pos=Pos(text3.absolute_rect.midtop) + (0, 75),
                           color=WHITESMOKE,
                           anchor=CENTER)

        yes_button = Button(text="Yeah, sure!",
                            function=self.agree,
                            shape=RoundedRect((200, 50), 100, border=0),
                            color=WHITESMOKE,
                            bg_color=MultiGradient(BLUE, GREEN, YELLOW, ORANGE),
                            pos=Pos(back_box.absolute_rect.midbottom) - Pos(back_box.absolute_rect.size[0], 0) / 4,
                            anchor=CENTER,
                            shadow=Shadow())

        no_button = Button(text="Nope",
                           function=self.disagree,
                           shape=RoundedRect((200, 50), 100),
                           color=WHITESMOKE,
                           bg_color=MultiGradient(RED, PINK, PURPLE),
                           pos=Pos(back_box.absolute_rect.midbottom) + Pos(back_box.absolute_rect.size[0], 0) / 4,
                           anchor=CENTER)

        widgets = [
            back_box,
            SimpleText(text="Do you agree?",
                                 pos=Pos(back_box.absolute_rect.midtop) - (0, 20),
                                 anchor=BOTTOM,
                                 color=WHITESMOKE,
                                 # underline_color=MultiGradient(*RAINBOW),
                                 font=default_font(105)),
            text1, text2, text3, text4,
            yes_button, no_button,
        ]

        super().__init__(app, widgets, (20, 10, 0))

    def agree(self):
        CONFIG.send_log = True
        CONFIG.first_time_launch = False
        self.app.set_screen(MENU)

    def disagree(self):
        CONFIG.send_log = False
        CONFIG.first_time_launch = False
        self.app.set_screen(MENU)
