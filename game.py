from graphalama.app import Screen

from physics import AABB
from player import Player


class GameScreen(Screen):
    def __init__(self, app, level=None):
        self.level = level
        self.player = Player()
        self.space = level.space
        self.space.add(self.player)
        self.ground = AABB((0, 500), (1500, 500))
        self.space.add(self.ground)

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
        surf.fill( (0, 0, 0), self.ground.pygame_rect)
        self.player.render(surf)