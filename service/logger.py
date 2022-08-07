from sys import stdout

from loguru import logger

from config import SOURCE_DIR_PATH


_format = '{time:YYYY:MM:DD:HH:mm:ss:SSS} | <level>{level: <8}</level> | {module}:{function}:{line} - ' \
          '<level>{message}</level>'
logger.remove(0)
logger.add(
    stdout,
    format=_format,
    level='DEBUG',
    enqueue=True,
)
logger.add(
    SOURCE_DIR_PATH + '/logs/server.log',
    format=_format,
    level='DEBUG',
    enqueue=True,
    rotation='1 MB',
    compression='zip',
)
