import pygame
import time
from graphalama.app import Screen

from idle_screen import IdleScreen
from player import Player
from level import Level
from constants import PICKER
from config import CONFIG, LEVELS
from physics import Pos
from widgets import Title, ResumeButton, QuitButton, MenuButton, PauseButton


class PauseScreen(IdleScreen):
    def __init__(self, app, game_screen_paused):
        self.paused_game = game_screen_paused  # Type: GameScreen

        size = Pos(app.display.get_size())
        widgets = [
            Title("Paused", size),
            ResumeButton(self.paused_game.resume, size / 2 - (0, 65)),
            MenuButton(app, size / 2),
            QuitButton(app, size / 2 + (0, 65)),
        ]

        super().__init__(app, widgets, (0, 0, 0))

    def update(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.paused_game.resume()
        else:
            super().update(event)

    def draw_background(self, display):
        self.paused_game.render(display)

        super().draw_lamas(display)


class GameScreen(Screen):
    FPS = 60

    def __init__(self, app, level):
        size = Pos(app.display.get_size())
        self.level = level
        self.player = Player(self.level.world_start)
        self.space = self.level.space
        self.space.add(self.player)
        self.start_time = time.time()
        self.pause_time = 0

        widgets = [
            PauseButton(self.pause, (size[0] - 30, 30)),
        ]

        super().__init__(app, widgets, bg_color=(0, 165, 255))

    def pause(self):
        """ Pause the game by going into PauseScreen """
        self.pause_time = time.time()
        self.app.set_temp_screen(lambda sm: PauseScreen(sm, self))

    def resume(self):
        """ Resume the game after a PauseScreen """
        self.app.set_temp_screen(self)
        self.start_time += (time.time() - self.pause_time)

    def update(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.pause()
            return True
        if super().update(event):
            return True

        return self.player.update(event)

    def internal_logic(self):
        if self.level.over:
            run_time = time.time() - self.start_time
            level_stats = CONFIG.levels_stats[str(self.level.num)]
            if level_stats[1] == -1 or run_time < level_stats[1]:
                CONFIG.levels_stats[str(self.level.num)] = (level_stats[0], run_time)
            if CONFIG.level + 1 in LEVELS:
                CONFIG.level += 1
            self.app.set_screen(PICKER)
        elif self.level.to_reset:
            self.level = Level.load_num(self.level.num)
            self.player = Player(self.level.world_start, respawn=True)
            self.space = self.level.space
            self.space.add(self.player)
            self.start_time = time.time()
            level_stats = CONFIG.levels_stats[str(self.level.num)]
            CONFIG.levels_stats[str(self.level.num)] = (level_stats[0] + 1, level_stats[1])
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
