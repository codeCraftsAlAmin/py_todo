import sys

from loguru import logger

# remove deafult handler to remvoe duplicate log
logger.remove()

# to show colorful output
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG",
)

# auto rotation for production or local file (create a new file if the file size excedes 10mb and then the last files will be deleted after 10days)
logger.add(
    "logs/app_error.log",
    rotation="10 MB",
    retention="10 days",
    level="ERROR",
    compression="zip",
    enqueue=True,  # for multiprocess or asynchronous safety
)

# we are gonna import this logger file in our entire project
