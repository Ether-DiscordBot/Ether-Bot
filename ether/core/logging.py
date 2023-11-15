import logging

from ether.core.config import config


class EtherFormatter(logging.Formatter):

    blue = "\x1b[34;20m"
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    format_string = (
        "%(asctime)s %(levelname)-8s [%(filename)20s:%(lineno)-4s] %(message)s"
    )
    FORMATS = {
        logging.DEBUG: blue + format_string + reset,
        logging.INFO: blue + format_string + reset,
        logging.WARNING: yellow + format_string + reset,
        logging.ERROR: red + format_string + reset,
        logging.CRITICAL: bold_red + format_string + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
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


log = setup_logger("ether", config.get("logLevel"))
setup_logger("werkzeug")
setup_logger("discord")
