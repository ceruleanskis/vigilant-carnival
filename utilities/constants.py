import os

VERSION = "0.1.0"
GAME_NAME = "mygame"
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# todo: make platform agnostic (right now, it's linux only paths)
USER_DIR = os.path.expanduser('~')
APPLICATION_DATA = os.environ.get("XDG_DATA_HOME", )
SAVE_GAME_DIR = f'{USER_DIR}/.local/share/{GAME_NAME}/saves'
SAVE_GAME_PREFIX = 'data'
SAVE_GAME_EXT = '.save.json'

DISPLAY_WIDTH = 1920
DISPLAY_HEIGHT = 1080
FPS = 60
DEBUG = True
GRID_DISPLAY = False
COORDINATE_DISPLAY = False
FPS_DISPLAY = True
TILE_SIZE = 40
FOG_OF_WAR_ON = False

BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

DARK_BLUE = (100, 130, 161)

TILES = []
TILE_FLOOR = 'floor'
TILE_WALL = 'wall'
TILE_STONE = 'stone'
TILE_DOOR = 'door'
TILE_OPEN_DOOR = 'open_door'
