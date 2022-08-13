import sys
from loguru import logger

logger.remove()
logger.add(
    sink=sys.stdout,
    colorize=True,
    level='DEBUG',
    format="<cyan>{time:DD.MM.YYYY HH:mm:ss}</cyan> | <level>{level}</level> | <magenta>{message}</magenta>",
)
