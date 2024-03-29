"""
Sets global seed variables for use with the random module.
Checks for the env variable GAME_SEED; if not present, generates a new seed.
"""

import os
import uuid

import utilities.logsetup

log = utilities.logsetup.log()


def generate_new_seed() -> None:
    """
    Generate a new seed using uuid4. Sets the seed global value and its integer representation as seed_int.
    
    :return:
    :rtype: None
    """
    log.info('Generating new seed...')
    global seed
    global seed_int
    seed = uuid.uuid4()
    seed_int = seed.int


def import_seed(seed_uuid: str) -> None:
    """
    Given a uuid str (with or without dashes), sets the seed global value to the seed_uuid and its integer
    representation as seed_int.

    :param seed_uuid: A string representing a uuid value
    :type seed_uuid: str
    :return:
    :rtype: None
    """
    try:
        log.info('Importing seed...')
        global seed
        global seed_int
        seed = uuid.UUID(seed_uuid)
        seed_int = seed.int
        log.info(f'Imported seed {seed}')
    except Exception as err:
        log.warning(f'Importing seed from env failed: {err} \n'
                    f'Generating new seed...')
        generate_new_seed()


seed_from_env = os.getenv('GAME_SEED', None)
seed: uuid.UUID = None
seed_int: int = None
if seed_from_env is None:
    generate_new_seed()
else:
    log.info(f'GAME_SEED: {seed_from_env}')
    import_seed(seed_from_env)

log.info(f'Seed: {seed}, {seed_int}')
