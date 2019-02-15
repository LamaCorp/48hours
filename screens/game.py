import os
import logging
import pygame
from time import time

from graphalama.app import Screen
from graphalama.colors import ImageBrush

from screens.idle_screen import IdleScreen
from player import Player
from level import Level
from constants import PICKER, LEVELS_GRAPHICAL_FOLDER
from config import CONFIG, LEVELS
from physics import Pos
from screens.widgets import Title, ResumeButton, QuitButton, MenuButton, PauseButton

LOGGER = logging.getLogger(__name__)


class PauseScreen(IdleScreen):
    def __init__(self, app, game_screen_paused):
        LOGGER.info("Entered pause screen")
        self.paused_game = game_screen_paused  # type: GameScreen

        size = Pos(app.display.get_size())
        widgets = [
            Title("Paused", size),
            ResumeButton(self.paused_game.resume, size / 2 - (0, 65)),
            MenuButton(app, size / 2),
            QuitButton(app, size / 2 + (0, 65)),
        ]

        super().__init__(app, widgets, (0, 0, 0))

    def update(self, event):
        self.paused_game.player.update(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.paused_game.resume()
        else:
            super().update(event)

    def draw_background(self, display):
        self.paused_game.render(display)

        super().draw_lamas(display)


class GameScreen(Screen):
    FPS = 600
    UPDATE_FPS = 60

    def __init__(self, app, level):
        LOGGER.info("Entered game screen")
        LOGGER.info(f"Level is {level.num}")
        size = Pos(app.display.get_size())
        self.level = level
        self.player = Player(self.level.world_start)
        self.space = self.level.space
        self.space.add(self.player)
        self.start_time = time()
        self.pause_time = 0
        self.level.update_offset(self.level.world_start, size)
        self.black_screen = pygame.Surface(app.display.get_size())
        self.black_screen.fill((0, 0, 0))

        widgets = [
            PauseButton(self.pause, (size[0] - 30, 30)),
        ]
        bg = pygame.image.load(os.path.join(LEVELS_GRAPHICAL_FOLDER, 'bg.png'))
        for i in range(2):
            bg = pygame.transform.scale2x(bg)

        bg = ImageBrush(bg)
        super().__init__(app, widgets, bg_color=bg)
        self.fade_out_black()

        self.last_internal_logic = time()
        self.internal_logic_dt = 0

    def pause(self):
        """ Pause the game by going into PauseScreen """
        LOGGER.info("Pausing the game by going into PauseScreen")
        self.pause_time = time()
        self.app.set_temp_screen(lambda sm: PauseScreen(sm, self))

    def resume(self):
        """ Resume the game after a PauseScreen """
        LOGGER.info("Resuming the game after a PauseScreen")
        self.app.set_temp_screen(self)
        self.start_time += (time() - self.pause_time)

    def update(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.pause()
            return True
        if super().update(event):
            return True

        return self.player.update(event)

    def internal_logic(self):
        # The goal is to have constant update frame rate -> constant player speed
        self.internal_logic_dt += time() - self.last_internal_logic
        self.last_internal_logic = time()

        while self.internal_logic_dt > 1 / self.UPDATE_FPS:
            self.internal_logic_dt -= 1 / self.UPDATE_FPS
            self._internal_logic()

    def _internal_logic(self):
        if self.level.over:
            self.fade_in_black()
            LOGGER.info(f"Level is over. Level was {self.level.num}")
            if str(CONFIG.level + 1) in LEVELS:
                CONFIG.level += 1
            level_stats = CONFIG.levels_stats[str(self.level.num)]
            run_time = time() - self.start_time
            if level_stats[1] == -1 or run_time < level_stats[1]:
                CONFIG.levels_stats[str(self.level.num)][1] = run_time
            self.app.set_screen(PICKER)
        elif self.level.to_reset:
            LOGGER.info("Level is resetting (it means the player died, in case you weren't aware of that)")
            self.fade_in_black()
            self.level = Level.load_num(self.level.num)
            self.player = Player(self.level.world_start, respawn=True)
            self.space = self.level.space
            self.space.add(self.player)
            self.level.update_offset(self.level.world_start, self.app.display.get_size())
            CONFIG.levels_stats[str(self.level.num)][0] += 1
            self.fade_out_black()
            self.start_time = time()
        elif self.level.exploding:
            # Saving run time if best
            # Actually explode
            self.level.internal_logic()
        else:
            self.space.simulate()
            self.level.update_offset(self.player.center, self.app.display.get_size())
            self.level.internal_logic()

        fps = round(self.app.clock.get_fps())
        if fps < 50 and not self.level.to_reset:
            LOGGER.debug(f"Low FPS: {fps}")

    def render(self, surf):
        self.draw_background(surf)

        self.level.render(surf)
        self.widgets.render(surf)

        # De-comment to see hitbox
        # self.space.debug_draw(surf, -self.level.offset)

    def fade_in_black(self):
        for a in range(0, 255, 15):
            self.black_screen.set_alpha(a)
            self.render(self.app.display)
            self.app.display.blit(self.black_screen, (0, 0))
            pygame.display.flip()

    def fade_out_black(self):
        for a in range(255, -1, -15):
            self.black_screen.set_alpha(a)
            self.render(self.app.display)
            self.app.display.blit(self.black_screen, (0, 0))
            pygame.display.flip()
