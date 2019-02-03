from graphalama.app import Screen

from player import Player
from level import Level
from constants import PICKER
from config import LevelConfig, LEVELS


class GameScreen(Screen):
    def __init__(self, app, level):
        self.level = level
        self.player = Player(self.level.world_start)
        self.space = self.level.space
        self.space.add(self.player)

        super().__init__(app, bg_color=(0, 165, 255))

    def update(self, event):
        if super().update(event):
            return True

        return self.player.update(event)

    def internal_logic(self):
        if self.level.over:
            if LevelConfig.chosen_level + 1 in LEVELS:
                LevelConfig.chosen_level += 1
            self.app.set_screen(PICKER)
        elif self.level.to_reset:
            self.level = Level(self.level.num)
            self.player = Player(self.level.world_start, respawn=True)
            self.space = self.level.space
            self.space.add(self.player)
        else:
            self.space.simulate()
            self.level.update_offset(self.player.center, self.app.display.get_size())
            self.level.internal_logic()

    def render(self, surf):
        super().render(surf)

        self.level.render(surf)
        # self.space.debug_draw(surf, -self.level.offset)
