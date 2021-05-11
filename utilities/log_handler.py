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
        if hasattr(record, 'color'):
            color = record.__getattribute__('color')
        else:
            color = None

        if record.levelname == 'INFO':
            color = (utilities.constants.LIGHT_GREEN if color is None else color)
            utilities.messages.message_log.add_message(utilities.messages.Message(record.message, color))
        if record.levelname != 'INFO' and utilities.constants.DEBUG:
            if record.levelname == 'DEBUG':
                color = (utilities.constants.GREEN if color is None else color)
            elif record.levelname == 'ERROR':
                color = (utilities.constants.RED if color is None else color)
            elif record.levelname == 'CRITICAL':
                color = (utilities.constants.ORANGE if color is None else color)
            elif record.levelname == 'WARNING':
                color = (utilities.constants.YELLOW if color is None else color)

            color = (utilities.constants.WHITE if color is None else color)
            utilities.messages.message_log.add_message(utilities.messages.Message(record.message, color))
