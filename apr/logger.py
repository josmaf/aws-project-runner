import logging
import sys
from colorlog import ColoredFormatter

LOG_LEVEL = logging.INFO
LOGFORMAT = "  %(log_color)s%(asctime)s [%(levelname)s] | %(log_color)s%(message)s%(reset)s"

stream = logging.StreamHandler(sys.stdout)
stream.setLevel(LOG_LEVEL)
stream.setFormatter(ColoredFormatter(LOGFORMAT))

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("debug.log"), stream]
)


def get_logger(logger_name):
    return logging.getLogger(logger_name)
