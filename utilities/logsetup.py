import logging.config
import os
import utilities.constants

# DEBUG - Detailed information, typically of interest only when diagnosing problems.
# INFO - Confirmation that things are working as expected.
# WARNING - An indication that something unexpected happened, or indicative of some problem in the near future
# (e.g. ‘disk space low’). The software is still working as expected.
# ERROR - Due to a more serious problem, the software has not been able to perform some function.
# CRITICAL - A serious error, indicating that the program itself may be unable to continue running.

def log() -> logging.Logger:
    """
    Create a logger that outputs to a file and uses the logutil conf file

    :return: Returns the logger.
    :rtype: Logger
    """
    _dir = utilities.constants.ROOT_DIR
    log_file_path = os.path.join(_dir, 'logutil.conf')
    logging.config.fileConfig(log_file_path, disable_existing_loggers=False)
    logger = logging.getLogger()
    return logger
