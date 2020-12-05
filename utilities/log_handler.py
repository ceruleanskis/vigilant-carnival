import logging.handlers
import os

import utilities.constants


def mkdir_p(path):
    os.makedirs(path, exist_ok=True)  # Python>3.2


class MakeFileHandler(logging.handlers.RotatingFileHandler):
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=False):
        filepath = f'{utilities.constants.LOG_DIR}/{filename}'
        mkdir_p(utilities.constants.LOG_DIR)
        logging.handlers.RotatingFileHandler.__init__(self, filepath, mode, maxBytes, backupCount, encoding, delay)
