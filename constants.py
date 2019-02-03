import os

# Screens
MENU = 0
GAME = 42
SETTINGS = 67140
PICKER = 93933
STATS = 67115

# Colors
DARK = (31, 32, 65)
LIGHT_DARK = (62, 64, 130)

# Folder
ASSETS = os.path.abspath(os.path.join(os.path.dirname(__file__), 'assets'))
PLAYER_FOLDER = os.path.join(ASSETS, 'players')
LEVELS_FOLDER = os.path.join(ASSETS, 'levels')
LEVELS_GRAPHICAL_FOLDER = os.path.join(LEVELS_FOLDER, 'graphical')
MAPS_FOLDER = os.path.join(LEVELS_FOLDER, 'maps')

# Blocks
DEFAULT_BLOCK_SIZE = 32
START = "P"

# Physical constant
BROCHETTE_VELOCITY = 15

# Brochettes
FRAME_BEFORE_DESPAWN = 30
