import os
import datetime
import logging
import logging.handlers


new_log_path = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'logs',
    f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
)

# create the logger
logger = logging.getLogger('Surf')
logger.setLevel(logging.DEBUG)

# create a formatter
formatter = logging.Formatter('%(asctime)s %(name)s %(filename)30s  %(funcName)35s %(lineno)3s %(levelname)8s: %(message)s')

# create rotating file handler
file_handler = logging.handlers.RotatingFileHandler(
    new_log_path,
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

logger.info('-'*len(f'logging to: {new_log_path}'))
logger.info('logger ready.')
logger.info(f'logging to: {new_log_path}')
logger.info('-'*len(f'logging to: {new_log_path}'))
logger.info('')
