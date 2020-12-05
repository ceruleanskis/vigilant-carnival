import json

import utilities.constants
import utilities.logsetup
log = utilities.logsetup.log()

TILE_DATA = None
ENTITY_DATA = None

with open(f'{utilities.constants.ROOT_DIR}/assets/json/tiles.json') as json_file:
    TILE_DATA = json.load(json_file)
log.info(f'Loaded assets/json/tiles.json.')

with open(f'{utilities.constants.ROOT_DIR}/assets/json/entities.json') as json_file:
    ENTITY_DATA = json.load(json_file)
log.info(f'Loaded assets/json/entities.json.')
