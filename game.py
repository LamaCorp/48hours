import pygame
from graphalama.app import Screen

from player import Player
from level import Level
from constants import PICKER
from config import CONFIG, LEVELS
from physics import Pos
from widgets import Title, ResumeButton, QuitButton, MenuButton, PauseButton


class PauseScreen(Screen):
    FPS = 30

    def __init__(self, app, game_screen_paused):
        self.paused_game = game_screen_paused  # Type: GameScreen

        size = Pos(app.display.get_size())
        widgets = [
            Title("Paused", size),
            ResumeButton(self.paused_game.resume, size / 2 - (0, 65)),
            MenuButton(app, size / 2),
            QuitButton(app, size / 2 + (0, 65)),
        ]
        self.lama_logo = pygame.image.load('assets/players/lama_normal.png').convert()
        self.lama_logo.set_colorkey((255, 0, 255))
        for _ in range(4):
            self.lama_logo = pygame.transform.scale2x(self.lama_logo)
        self.lama_logo_left = pygame.transform.flip(self.lama_logo, True, False)

        super().__init__(app, widgets)

    def update(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.paused_game.resume()
        else:
            super().update(event)

    def draw_background(self, display):
        super().draw_background(display)

        self.paused_game.render(display)

        rect = self.lama_logo.get_rect()
        ss = self.app.display.get_size()
        rect.center = (ss[0] // 5, ss[1] // 2)
        display.blit(self.lama_logo, rect)
        rect.center = (ss[0] * 4/5, ss[1] // 2)
        display.blit(self.lama_logo_left, rect)


class GameScreen(Screen):
    def __init__(self, app, level):
        size = Pos(app.display.get_size())
        self.level = level
        self.player = Player(self.level.world_start)
        self.space = self.level.space
        self.space.add(self.player)

        widgets = [
            PauseButton(self.pause, size - (50, 30)),
        ]

        super().__init__(app, widgets, bg_color=(0, 165, 255))

    def pause(self):
        """ Pause the game by going into PauseScreen """
        self.app.set_temp_screen(lambda sm: PauseScreen(sm, self))

    def resume(self):
        """ Resume the game after a PauseScreen """
        self.app.set_temp_screen(self)

    def update(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.pause()
            return True
        if super().update(event):
            return True

        return self.player.update(event)

    def internal_logic(self):
        if self.level.over:
            if CONFIG.level + 1 in LEVELS:
                CONFIG.level += 1
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

        fps = round(self.app.clock.get_fps())
        if fps < 50:
            print(f"\033[31mLOW FPS: {fps}\033[m")

    def render(self, surf):
        self.draw_background(surf)

        self.level.render(surf)
        self.widgets.render(surf)

        # De-comment to see hitbox
        # self.space.debug_draw(surf, -self.level.offset)
