from logging import Formatter, getLogger, DEBUG, INFO, WARNING, ERROR, CRITICAL
from logging.config import dictConfig
import inspect
from sys import stdout, exit

from silo import config


class CustomFormatter(Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "[%(levelname)s] (%(module)s) %(asctime)s - %(message)s"

    FORMATS = {
        DEBUG: yellow + format + reset,
        INFO: grey + format + reset,
        WARNING: yellow + format + reset,
        ERROR: red + format + reset,
        CRITICAL: bold_red + format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = Formatter(log_fmt)
        return formatter.format(record)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {"format": "[%(levelname)s] (%(module)s) %(asctime)s - %(message)s"},
        "stdout_formatter": {"()": CustomFormatter},
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "stream": stdout,
            "formatter": "stdout_formatter",
            "level": config.log_level,
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": config.log_directory + "/silo.log",
            "formatter": "default",
            "level": config.log_level,
            "mode": "a",
        },
    },
    "loggers": {
        "silo": {
            "handlers": ["file", "stdout"],
            "level": "DEBUG",
            "propagate": True,
        }
    },
}
try:
    dictConfig(LOGGING_CONFIG)
    print(f"[APPLICATION LOGGING] Log file: {config.log_directory}/silo.log")
except ValueError as e:
    print(f"[ERROR] Cannot configure application logging!!! {e}")
    print("Exiting...")
    exit(1)

logger = getLogger("silo")

def api_logger(message: str):
    caller = inspect.stack()[1][3]
    logger.info("[%s] %s",  str(caller), message, stacklevel=2)