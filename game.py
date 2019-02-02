from graphalama.app import Screen

from player import Player


class GameScreen(Screen):
    def __init__(self, app, level):
        self.level = level
        self.player = Player(level.world_start)
        self.space = level.space
        self.space.add(self.player)

        super().__init__(app, bg_color=(0, 165, 255))

    def update(self, event):
        if super().update(event):
            return True

        return self.player.update(event)

    def internal_logic(self):
        self.player.internal_logic()
        self.space.simulate()

    def render(self, surf):
        super().render(surf)

        self.level.render(surf)
        self.player.render(surf)
