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
        self.space.simulate()
        self.level.update_offset(self.player.center, self.app.display.get_size())
        self.level.internal_logic()

    def render(self, surf):
        super().render(surf)


        self.level.render(surf)
        # self.space.debug_draw(surf, -self.level.offset)
