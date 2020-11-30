import json

import utilities.constants

TILE_DATA = None
ENTITY_DATA = None

with open(f'{utilities.constants.ROOT_DIR}/assets/json/tiles.json') as json_file:
    TILE_DATA = json.load(json_file)

with open(f'{utilities.constants.ROOT_DIR}/assets/json/entities.json') as json_file:
    ENTITY_DATA = json.load(json_file)
