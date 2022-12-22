import logging


class Formatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    format_string = (
        "%(asctime)s %(levelname)-8s [%(filename)20s:%(lineno)-4s] %(message)s"
    )
    FORMATS = {
        logging.DEBUG: grey + format_string + reset,
        logging.INFO: grey + format_string + reset,
        logging.WARNING: yellow + format_string + reset,
        logging.ERROR: red + format_string + reset,
        logging.CRITICAL: bold_red + format_string + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


log = logging.getLogger("ether_log")
log.setLevel(logging.DEBUG)

formatter = Formatter()

stream = logging.StreamHandler()
stream.setFormatter(formatter)
log.addHandler(stream)

file = logging.FileHandler("logs.log")

log.addHandler(file)
