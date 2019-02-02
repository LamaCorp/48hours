from graphalama.app import Screen

from player import Player


class GameScreen(Screen):
    def __init__(self, app, level=None):
        self.level = level
        self.player = Player()
        self.space = level.space
        self.space.add(self.player)

        super().__init__(app, (), bg_color=(0, 165, 255))

    def internal_logic(self):
        self.space.simulate()

    def render(self, surf):
        super().render(surf)

        self.level.render(surf)
        self.player.render(surf)