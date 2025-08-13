import logging
from config import config
from utils.config_helper import ConfigHelper

color = ConfigHelper().config_color

# Map the string to logging level
LOGGING_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

# Color mapping for different log levels
LEVEL_COLORS = {
    "DEBUG": "blue",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "red",
}


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log levels"""

    def format(self, record):
        # Get the original format
        log_entry = super().format(record)

        # Color the levelname if it exists in our color mapping
        levelname = record.levelname
        if levelname in LEVEL_COLORS:
            colored_level = color(levelname, LEVEL_COLORS[levelname])
            # Replace the levelname in the formatted string
            log_entry = log_entry.replace(levelname, colored_level)
        return log_entry


logging_format = "%(levelname)-9s | %(asctime)-20s | %(funcName)-35s  | %(filename)s:%(lineno)s \n%(message)s\n"

# Create custom formatter
formatter = ColoredFormatter(
    fmt=logging_format,
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Configure logging with custom formatter
logging.basicConfig(
    level=LOGGING_LEVELS.get(config.logging_level, logging.INFO),
    format=logging_format,
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Get the root logger and set our custom formatter
root_logger = logging.getLogger()
for handler in root_logger.handlers:
    handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
