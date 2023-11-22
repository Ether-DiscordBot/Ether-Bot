import logging

import wavelink

from ether.core.config import config


class EtherFormatter(logging.Formatter):

    pink = "\x1b[35;20m"
    blue = "\x1b[34;20m"
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    bold = "\x1b[1m"

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
