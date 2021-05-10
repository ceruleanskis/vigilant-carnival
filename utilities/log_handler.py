import logging
import logging.handlers
import os

import utilities.constants
import utilities.messages


def mkdir_p(path):
    os.makedirs(path, exist_ok=True)  # Python>3.2


class MakeFileHandler(logging.handlers.RotatingFileHandler):
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=False):
        filepath = f'{utilities.constants.LOG_DIR}/{filename}'
        mkdir_p(utilities.constants.LOG_DIR)
        logging.handlers.RotatingFileHandler.__init__(self, filepath, mode, maxBytes, backupCount, encoding, delay)


class InGameLogHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        if record.levelname == 'INFO':
            utilities.messages.message_log.add_message(utilities.messages.Message(record.message, utilities.constants.LIGHT_GREEN))
        if record.levelname != 'INFO' and utilities.constants.DEBUG:
            color = utilities.constants.WHITE
            if record.levelname == 'DEBUG':
                color = utilities.constants.GREEN
            elif record.levelname == 'ERROR':
                color = utilities.constants.RED
            elif record.levelname == 'CRITICAL':
                color = utilities.constants.ORANGE
            elif record.levelname == 'WARNING':
                color = utilities.constants.YELLOW

            utilities.messages.message_log.add_message(utilities.messages.Message(record.message, color))
