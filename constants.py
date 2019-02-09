import os

VERSION = "1.0"

# Screens
MENU = 0
GAME = 42
SETTINGS = 67140
PICKER = 93933
STATS = 67115
KEY_BIND = 1008
USER_AGREE = 31337

# Colors
DARK = (31, 32, 65)
LIGHT_DARK = (62, 64, 130)
DARK_GREY = (30, 30, 30,)

# Folder
ASSETS = os.path.abspath(os.path.join(os.path.dirname(__file__), 'assets'))
LOGFILE = os.path.join(ASSETS, "48hours.log")
PLAYER_FOLDER = os.path.join(ASSETS, 'players')
LEVELS_FOLDER = os.path.join(ASSETS, 'levels')
LEVELS_GRAPHICAL_FOLDER = os.path.join(LEVELS_FOLDER, 'graphical')
MAPS_FOLDER = os.path.join(LEVELS_FOLDER, 'maps')
KEYS_FOLDER = os.path.join(ASSETS, 'keys')

# Blocks
DEFAULT_BLOCK_SIZE = 32
START = "P"

# Physical constant
BROCHETTE_VELOCITY = 15

# Brochettes
FRAME_BEFORE_DESPAWN = 30
