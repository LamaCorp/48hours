#!/usr/bin/env python3

from functools import partial

import click
from graphalama.app import Screen, App
from graphalama.buttons import CarouselSwitch, Button, ImageButton
from graphalama.colors import ImageBrush
from graphalama.constants import CENTER
from graphalama.core import Widget
from graphalama.shapes import Rectangle
import pygame

from blocks import Block, BLOCKS, Stone
from constants import DEFAULT_BLOCK_SIZE, MAPS_FOLDER
from entities import OBJECTS, Spawn, SPAWN
from level import Level
from physics import Pos

pygame.init()

MAP_SIZE = (120, 40)
LEVEL_NAME = "fail"


class LevelEdit(Level):

    def __init__(self):
        super().__init__()
        self.path = ''
        self.img_cache = {}


    @classmethod
    def load(cls, path, size=(120, 40)):
        try:
            level = cls.load_v1(path)
            level.path = path
            return level
        except:
            print('Can not load as v1')


        try:
            level = cls.load_v2(path, is_editor=True)
            level.path = path
            return level
        except:
            print('Can not load as v2')
            print("Creating new level")
            raise

        level = cls()
        level.size = Pos(size)
        level.objects = [Spawn((size[0] // 2, size[1] // 2))]

        for y in range(0, size[1]):
            line = []
            for x in range(0, size[0]):
                if y == size[1] - 1:
                    line.append(Block.new("B", (x, y)))
                elif x in (0, size[0] - 1) or y == 0:
                    line.append(Stone((x, y)))
                else:
                    line.append(Block((x, y)))
            level.grid.append(line)
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
        if 0 <= pos[0] < self.size[0] and 0 <= pos[1] < self.size[1]:
            block = BLOCKS[block](pos=pos)
            self.grid[pos[1]][pos[0]] = block
            self.clean_cache_around(pos)

    def erase(self, pos):
        self.grid[pos[1]][pos[0]] = Block(pos)
        for obj in self.objects[:]:
            if obj.pos == pos:
                self.objects.remove(obj)
                try:
                    self.space.projectiles.remove(obj)
                except ValueError:
                    pass

        self.clean_cache_around(pos)

    def add_object(self, pos, object):
        if isinstance(object, Spawn):
            for o in self.objects[:]:
                if isinstance(o, Spawn):
                    self.objects.remove(o)

        else:
            for o in self.objects:
                # Don't add twice the same object at the same position
                if isinstance(o, type(object)) and o.pos == pos:
                    return

        object.pos = pos
        self.objects.append(object)

    def clear(self):
        for y, line in enumerate(self.grid):
            for x, _ in enumerate(line):
                self.grid[y][x] = Block.new('.', (x, y))

        self.objects.clear()
        self.space.projectiles.clear()  # we we load, object like AK47 are directly added in this list
        self.img_cache.clear()

    def render(self, surf):
        super().render(surf)
        for obj in self.objects:
            pos = self.map_to_display(obj.pos)
            surf.blit(obj.img, pos)


EDIT = 1


class EditScreen(Screen):
    BRUSH = 1
    OBJECTBRUSH = 2
    ERASER = 3

    def __init__(self, app):
        self.start_drag = None
        self.start_drag_map_pos = None
        self.level = LevelEdit.load(LEVEL_NAME, MAP_SIZE)  # type: LevelEdit

        self.menu_width = 240

        # widgets
        self.widget_bg = Widget((0, 0), (self.menu_width, app.SCREEN_SIZE[0]), bg_color=(200, 200, 200))
        self.tool_carousel = CarouselSwitch(["Brush", "ObjectBrush", "Eraser"],  self.tool_change, (20, 20),
                                            shape=(self.menu_width - 40, 40))
        reset = Button("Reset", self.reset, bg_color=(240, 100, 60))
        save = Button("Save", self.save)

        # tiles buttons
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

        # objects buttons
        objects = []
        for i, obj in enumerate(OBJECTS.values()):
            obj = obj()
            y, x = divmod(i, 5)
            pos = (self.menu_width - 40*x - 40,
                   app.SCREEN_SIZE[1] - 40 * y - 40)
            objects.append(ImageButton(partial(self.set_brush_object, obj.type),
                                       pos=pos,
                                       shape=Rectangle((32, 32)),
                                       color=ImageBrush(obj.img),
                                       anchor=CENTER))

        widgets = (self.widget_bg, self.tool_carousel, reset, save, *tiles, *objects)
        super().__init__(app, widgets, (20, 40, 90))

        # map
        self.tile_size = DEFAULT_BLOCK_SIZE
        self.level.offset.x += self.menu_width
        self._tile_index = 0
        self._object_index = SPAWN

        # editor settings
        self.drawing = False
        self.tool = self.BRUSH

        # Erase pic
        self.erase_img = pygame.Surface((DEFAULT_BLOCK_SIZE, DEFAULT_BLOCK_SIZE))
        self.bg_color.paint(self.erase_img)

    @property
    def tile_index(self):
        return self._tile_index

    @tile_index.setter
    def tile_index(self, value):
        self._tile_index = value % len(BLOCKS)

    @property
    def object_index(self):
        return self._object_index

    @object_index.setter
    def object_index(self, value):
        self._object_index = value  #  % len(OBJECTS)

    @property
    def current_tile(self):
        return BLOCKS[self.tile_index]()

    @property
    def current_object(self):
        return OBJECTS[self.object_index]()

    @property
    def current_img_under_cursor(self):
        if self.tool == self.BRUSH:
            return self.current_tile.get_img()
        elif self.tool == self.OBJECTBRUSH:
            return self.current_object.img
        elif self.tool == self.ERASER:
            return self.erase_img

    def set_brush_tile(self, i):
        self.tile_index = i
        self.tool = self.BRUSH

    def set_brush_object(self, i):
        self.object_index = i
        self.tool = self.OBJECTBRUSH

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
            elif event.key == pygame.K_o:
                self.tool_carousel.option_index = self.tool_carousel.options.index("ObjectBrush")

        if self.start_drag:
            self.level.offset = Pos(self.start_drag_map_pos) + 2*(self.start_drag - Pos(pygame.mouse.get_pos()))

    def internal_logic(self):
        if self.drawing:
            pos = pygame.mouse.get_pos()
            pos = self.level.display_to_map(pos)

            if self.tool == self.BRUSH:
                self.level.add_block(pos, self.tile_index)
            elif self.tool == self.ERASER:
                self.level.erase(pos)
            elif self.tool == self.OBJECTBRUSH:
                self.level.add_object(pos, self.current_object)

    def render(self, display):
        self.draw_background(display)

        self.level.render(display)

        # cursor
        img = self.current_img_under_cursor
        img = pygame.transform.scale(img, (self.tile_size, ) *2)
        img.set_alpha(128)
        pos = self.level.map_to_display(self.level.display_to_map(pygame.mouse.get_pos()))
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
        self.level.save(LEVEL_NAME)


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
@click.argument("width", default=120)
@click.argument("height", default=40)
def main(level_name, width, height):
    global LEVEL_NAME, MAP_SIZE

    LEVEL_NAME = MAPS_FOLDER + '/' + level_name + '.map'
    MAP_SIZE = (width, height)

    pygame.init()
    Apple().run()
    pygame.quit()


if __name__ == '__main__':
    main()
