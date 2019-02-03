#!/usr/bin/env python3

import json
from collections import defaultdict
from functools import lru_cache, partial
from typing import Dict, List

import click
import pygame;
from graphalama.colors import ImageBrush
from graphalama.constants import CENTER
from graphalama.shapes import Rectangle

pygame.init()
from graphalama.app import Screen, App
from graphalama.buttons import CarouselSwitch, Button, ImageButton
from graphalama.core import Widget

from blocks import Block, BLOCKS
from constants import LEVELS_FOLDER, DEFAULT_BLOCK_SIZE, MAPS_FOLDER
from level import Level
from physics import AABB, Pos

LEVEL_NAME = "fail"


class LevelEdit(Level):

    def __init__(self):
        super().__init__()
        self.path = ''
        self.img_cache = {}

    @classmethod
    def load(cls, path):
        try:
            level = cls.load_v1(path)
            level.path = path
            print(level)
            return level
        except:
            print('Can not load as v1')


        try:
            level = cls.load_v2(path)
            level.path = path
            return level
        except:
            print('Can not load as v2')

        print('Creating new level', path)

        level = cls()
        level.path = path

        return level

    @classmethod
    def load_v2(cls, path):
        with open(path, "r") as f:
            d = json.loads(f.read())
        size = Pos(d["size"])
        map = [
            [
                Block.new(c, (x, y))
                for x, c in enumerate(line)
            ]
            for y, line in enumerate(d["blocks"])
        ]
        objects = []

        level = cls()
        level.size = size
        level.grid = map

        return level


    def get_img_at(self, map_pos):
        x, y = map_pos
        if map_pos not in self.img_cache:
            neigh = "".join(self.get_block((x + dx, y + dy)).character
                            for dy in range(-1, 2)
                            for dx in range(-1, 2))
            block = self.get_block(map_pos)
            img = block.get_img(neigh, rotation=block.rotation)
            self.img_cache[map_pos] = img

        return self.img_cache[map_pos]

    def clean_cache_around(self, pos):
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                p = pos[0] + dx, pos[1] + dy
                if p in self.img_cache:
                    del self.img_cache[p]

    def add_block(self, pos, block):
        block = BLOCKS[block](pos=pos)
        self.grid[pos[1]][pos[0]] = block
        self.clean_cache_around(pos)

    def remove_block(self, pos):
        self.grid[pos[1]][pos[0]] = Block(pos)
        self.clean_cache_around(pos)

    def clear(self):
        for y, line in enumerate(self.grid):
            for x, _ in enumerate(line):
                self.grid[y][x] = Block.new('.', (x, y))

        self.img_cache.clear()

    def save(self):
        d = {}
        d["size"] = self.size.ti
        d["blocks"] = str(self).splitlines(keepends=False)
        d["objects"] = [obj.to_json() for obj in self.objects]
        d["version"] = 2

        s = json.dumps(d, indent=4)
        with open(LEVEL_NAME, "w") as f:
            f.write(s)

EDIT = 1


class EditScreen(Screen):
    BRUSH = 1
    ERASER = 2

    def __init__(self, app):
        self.start_drag = None
        self.start_drag_map_pos = None
        self.level = LevelEdit.load(LEVEL_NAME)  # type: LevelEdit
        self.objects = []

        self.menu_width = 240

        # widgets
        self.widget_bg = Widget((0, 0), (self.menu_width, app.SCREEN_SIZE[0]), bg_color=(200, 200, 200))
        self.tool_carousel = CarouselSwitch(["Brush", "Eraser"],  self.tool_change, (20, 20),
                                            shape=(self.menu_width - 40, 40))
        reset = Button("Reset", self.reset, bg_color=(240, 100, 60))
        save = Button("Save", self.save)
        tiles = []
        for i, block in enumerate(BLOCKS):
            block = block()
            y, x = divmod(i, 5)
            pos = (40 * x + 40,
                   40 * y + 170)
            tiles.append(ImageButton(partial(self.set_brush_tile, i),
                                     pos=pos,
                                     shape=Rectangle((32, 32), padding=0),
                                     color=ImageBrush(block.get_img()),
                                     anchor=CENTER))
        widgets = (self.widget_bg, self.tool_carousel, reset, save, *tiles)
        super().__init__(app, widgets, (20, 40, 90))

        # map
        self.tile_size = DEFAULT_BLOCK_SIZE
        self.level.offset.x += self.menu_width
        self._tile_index = 0

        # editor settings
        self.drawing = False
        self.tool = self.BRUSH

    @property
    def tile_index(self):
        return self._tile_index

    @tile_index.setter
    def tile_index(self, value):
        self._tile_index = value % len(BLOCKS)

    @property
    def current_tile(self):
        return BLOCKS[self.tile_index]()

    def set_brush_tile(self, i):
        self.tile_index = i

    def tool_change(self, tool_name: str):
        self.tool = getattr(self, tool_name.upper(), self.BRUSH)

    def update(self, event):
        if super(EditScreen, self).update(event):
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.drawing = True
            elif event.button == 2:
                self.drag()
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.drawing = False
            elif event.button == 2:
                self.drop()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.app.quit()
            elif event.key == pygame.K_r:
                self.reset()
            elif event.key == pygame.K_s:
                self.save()
            elif event.key == pygame.K_b:
                self.tool_carousel.option_index = self.tool_carousel.options.index("Brush")
            elif event.key == pygame.K_e:
                self.tool_carousel.option_index = self.tool_carousel.options.index("Eraser")
            elif event.key == pygame.K_MINUS:
                self.scale = min(self.scale - 1, 1)
            elif event.key == pygame.K_PLUS:
                self.scale += 1

        if self.start_drag:
            self.level.offset = Pos(self.start_drag_map_pos) + 2*(self.start_drag - Pos(pygame.mouse.get_pos()))

    def internal_logic(self):
        if self.drawing:
            pos = pygame.mouse.get_pos()
            pos = self.level.display_to_map(pos)

            if self.tool == self.BRUSH:
                self.level.add_block(pos, self.tile_index)
            elif self.tool == self.ERASER:
                self.level.remove_block(pos)

    def render(self, display):
        self.draw_background(display)

        self.level.render(display)

        # cursor
        img = self.current_tile.get_img()
        img = pygame.transform.scale(img, (self.tile_size, ) *2)
        img.set_alpha(128)
        pos = self.level.map_to_display(self.level.map_to_display(pygame.mouse.get_pos()))
        display.blit(img, (round(pos[0]), round(pos[1])))

        self.widgets.render(display)

    def drag(self):
        self.start_drag = pygame.mouse.get_pos()
        self.start_drag_map_pos = self.level.offset

    def drop(self):
        self.start_drag = None
        self.start_drag_map_pos = None

    def reset(self):
        self.level.clear()

    def save(self):
        self.level.save()


class Apple(App):
    SCREEN_SIZE = (1600, 1008)
    FPS = 30

    def __init__(self):
        screens = {
            EDIT: EditScreen
        }
        initial_screen = EDIT
        super().__init__(screens, initial_screen)
        self.display = pygame.display.set_mode(self.SCREEN_SIZE, pygame.RESIZABLE)


@click.command()
@click.argument("level_name")
def main(level_name):
    global LEVEL_NAME
    LEVEL_NAME = MAPS_FOLDER + '/' + level_name + '.map'

    pygame.init()
    Apple().run()
    pygame.quit()


if __name__ == '__main__':
    main()
