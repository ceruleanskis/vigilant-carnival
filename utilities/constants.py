import os

VERSION = "0.2.0"
GAME_NAME = "mygame"
DEBUG = True
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# todo: make platform agnostic (right now, it's linux only paths)
USER_DIR = os.path.expanduser('~')
APPLICATION_DATA = os.environ.get("XDG_DATA_HOME", )
LOCAL_SHARE = f'{USER_DIR}/.local/share'

if DEBUG:
    LOG_DIR = 'logs'
    SAVE_GAME_DIR = 'saves'
else:
    SAVE_GAME_DIR = f'{LOCAL_SHARE}/{GAME_NAME}/saves'
    LOG_DIR = f'{LOCAL_SHARE}/{GAME_NAME}/logs'

SAVE_GAME_PREFIX = 'data'
SAVE_GAME_EXT = '.save.json'

TILE_SIZE = 40

FONT_SIZE = 48
DISPLAY_WIDTH = 1920
DISPLAY_HEIGHT = 1080
MESSAGE_LOG_WIDTH = 1920
MAX_MESSAGES = 5
MESSAGE_LOG_HEIGHT = (FONT_SIZE + 5) * MAX_MESSAGES
MAP_DISPLAY_HEIGHT = ((DISPLAY_HEIGHT - MESSAGE_LOG_HEIGHT) // TILE_SIZE)
MAP_DISPLAY_WIDTH = DISPLAY_WIDTH // TILE_SIZE

FPS = 60
GRID_DISPLAY = False
COORDINATE_DISPLAY = False
FPS_DISPLAY = True
FOG_OF_WAR_ON = True

BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
WHITE = (255, 255, 255)

DARK_BLUE = (100, 130, 161)

TILES = []
TILE_FLOOR = 'floor'
TILE_WALL = 'wall'
TILE_STONE = 'stone'
TILE_DOOR = 'door'
TILE_OPEN_DOOR = 'open_door'
