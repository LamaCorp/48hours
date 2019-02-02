import os
import pygame
from physics import Space
from constants import LEVELS_GRAPHICAL_FOLDER, MAPS_FOLDER

# TODO: make dis a dictionnary
START = ("P", None)
EMPTY = (".", None)
# TODO: choose randomly between available textures
# TODO: remove grass and automatically add grass when there is no block over it
GRASS = ("G", pygame.image.load(os.path.join(LEVELS_GRAPHICAL_FOLDER, "grass_000.png")))
DIRT = ("D", pygame.image.load(os.path.join(LEVELS_GRAPHICAL_FOLDER, "dirt_000.png")))
STONE = ("S", pygame.image.load(os.path.join(LEVELS_GRAPHICAL_FOLDER, "stone_000.png")))


class Level:
    def __init__(self, level='level_0'):
        self.name = level
        self.space = Space(gravity=(0, 1))
        self.grid = []
        self.height = 0
        self.width = 0
        self.start = (0, 0)
        self.load_level()

    def load_level(self):
        with open(os.path.join(MAPS_FOLDER, self.name + ".map"), 'r') as map_file:
            height, width = list(map(int, map_file.readline().split()))
            self.height = height
            self.width = width
            for h in range(height):
                line = list(map_file.readline().strip())
                for i in range(len(line)):
                    if line[i] == "P":
                        line[i] = START
                        self.start = (h, i)
                    elif line[i] == ".":
                        line[i] = EMPTY
                    elif line[i] == "G":
                        line[i] = GRASS
                    elif line[i] == "D":
                        line[i] = DIRT
                    elif line[i] == "S":
                        line[i] = STONE
                    else:
                        print("yes")
                        print(line[i])
                        print("pouet")
                        raise Exception("Shit fuck")
                self.grid.append(line)

    def render(self, surf):
        size = surf.get_size()
        for line in range(len(self.grid)):
            for block in range(len(self.grid[line])):
                if self.grid[line][block] != START and self.grid[line][block] != EMPTY:
                    surf.blit(self.grid[line][block][1], (block * 17, line * 17))
