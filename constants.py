import os

# Screens
MENU = 0
GAME = 42
SETTINGS = "TODO"
PICKER = 93933

# Colors
DARK = (31, 32, 65)
LIGHT_DARK = (62, 64, 130)

# Folder
ASSETS = os.path.abspath(os.path.join(os.path.dirname(__file__), 'assets'))
PLAYER_FOLDER = os.path.join(ASSETS, 'players')
LEVELS_FOLDER = os.path.join(ASSETS, 'levels')
LEVELS_GRAPHICAL_FOLDER = os.path.join(LEVELS_FOLDER, 'graphical')
MAPS_FOLDER = os.path.join(LEVELS_FOLDER, 'maps')

DEFAULT_BLOCK_SIZE = 32
