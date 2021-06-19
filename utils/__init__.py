import os
import datetime
import logging
import logging.handlers
from pathlib import Path


def get_log_path() -> str:
    """Filepath of the next log file."""
    return os.path.join(LOGS_DIR, f"{START_TIME.strftime('%Y%m%d_%H%M%S')}.log")


def create_logger() -> logging.Logger:
    """Create """
    # create the logger
    logger = logging.getLogger('Surf')
    logger.setLevel(logging.DEBUG)

    # create a formatter
    formatter = logging.Formatter('%(asctime)s %(name)30s %(filename)20s  %(funcName)30s %(lineno)3s %(levelname)8s: %(message)s')

    if not os.path.isfile(LOG_FILE):
        open(LOG_FILE, 'w')

    # create rotating file handler
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=1000000,
        backupCount=30
    )
    file_handler.setFormatter(formatter)

    # create handler for stdout
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


def log_startup_details() -> None:
    """Log startup details helpful during debugging."""
    logger.info('-'*len(f'logging to: {LOG_FILE}'))
    logger.info('logger ready.')
    logger.info(f'logging to: {LOG_FILE}')
    logger.info('-'*len(f'logging to: {LOG_FILE}'))
    logger.debug(f'START_TIME:\t{START_TIME}')
    logger.debug(f'ROOT_DIR:\t{ROOT_DIR}')
    logger.debug(f'CONFIG_DIR:\t{CONFIG_DIR}')
    logger.debug(f'LOGS_DIR:\t{LOGS_DIR}')
    logger.debug(f'PROFILES_DIR:\t{PROFILES_DIR}')
    logger.debug(f'UI_DIR:\t\t{UI_DIR}')
    logger.debug(f'UI_KV_DIR:\t{UI_KV_DIR}')
    logger.debug(f'UI_PY_DIR:\t{UI_PY_DIR}')
    logger.info('-'*len(f'logging to: {LOG_FILE}'))
    logger.info('')
    logger.info('')
    logger.info('Running MDSurf.')
    logger.info('')


START_TIME = datetime.datetime.now()

# configuration outside of the poject
HOME_DIR = os.path.join(Path.home(), '.surf')
CONFIG_DIR = os.path.join(HOME_DIR, 'config')
LOGS_DIR = os.path.join(HOME_DIR, 'logs')
PROFILES_DIR = os.path.join(HOME_DIR, 'profiles')

# paths within the project
ROOT_DIR = Path(os.path.realpath(__file__)).parent.parent
UI_DIR = os.path.join(ROOT_DIR, 'interface')
UI_KV_DIR = os.path.join(UI_DIR, 'kv')
UI_PY_DIR = os.path.join(UI_DIR, 'baseclass')

LOG_FILE = get_log_path()
logger = create_logger() if os.path.isdir(LOGS_DIR) else None
