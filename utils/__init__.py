import os
import datetime
import logging
import logging.handlers
from pathlib import Path


def create_root_dirs():
    if not os.path.isdir(HOME_DIR):
        print(f'creating {HOME_DIR}')
        os.mkdir(HOME_DIR)
    if not os.path.isdir(PROFILES_DIR):
        print(f'creating {PROFILES_DIR}')
        os.mkdir(PROFILES_DIR)
    if not os.path.isdir(CONFIG_DIR):
        print(f'creating {CONFIG_DIR}')
        os.mkdir(CONFIG_DIR)
    if not os.path.isdir(LOGS_DIR):
        print(f'creating {LOGS_DIR}')
        os.mkdir(LOGS_DIR)


def get_log_path() -> str:
    """Filepath of the next log file."""
    return os.path.join(LOGS_DIR, f"{START_TIME.strftime('%Y%m%d_%H%M%S')}.log")


def create_logger() -> logging.Logger:
    """Create """
    # create the logger
    logger = logging.getLogger('Surf')
    logger.setLevel(logging.DEBUG)

    # create a formatter
    formatter = logging.Formatter('%(asctime)s %(name)20s %(filename)30s  %(funcName)35s %(lineno)3s %(levelname)8s: %(message)s')

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

create_root_dirs()
logger = create_logger()
log_startup_details()
