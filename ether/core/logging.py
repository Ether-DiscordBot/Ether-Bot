import logging

import wavelink
from colorama import just_fix_windows_console

just_fix_windows_console()

from ether.core.config import config


class EtherFormatter(logging.Formatter):

    pink = "\033[35;20m"
    blue = "\033[34;20m"
    grey = "\033[38;20m"
    yellow = "\033[33;20m"
    red = "\033[31;20m"
    bold_red = "\033[31;1m"
    reset = "\033[0m"
    bold = "\033[1m"

    @classmethod
    def format_string(cls, color):
        return f"{color}%(asctime)s {cls.bold} %(levelname)-8s {cls.pink}%(name)-10s{cls.reset}{color} [%(filename)20s:%(lineno)-4s] %(message)s {cls.reset}"

    FORMATS = {
        logging.DEBUG: grey,
        logging.INFO: blue,
        logging.WARNING: yellow,
        logging.ERROR: red + red,
        logging.CRITICAL: bold_red + bold_red,
    }

    def format(self, record):
        log_fmt = self.format_string(self.FORMATS.get(record.levelno))
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def setup_logger(logger_name: str, level=None) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    logger.setLevel(level if level else logging.WARNING)

    stream = logging.StreamHandler()
    stream.setFormatter(EtherFormatter())
    logger.addHandler(stream)

    file = logging.FileHandler("logs.log")
    logger.addHandler(file)

    return logger


log = setup_logger("ether_main", config.get("logLevel"))
db_log = setup_logger("ether_db", config.get("logLevel"))
setup_logger("werkzeug")
setup_logger("discord")
setup_logger(wavelink.__name__)
