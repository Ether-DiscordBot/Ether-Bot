import logging


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


log = logging.getLogger("ether")
werkzeug = logging.getLogger("werkzeug")
log.setLevel(logging.DEBUG)
werkzeug.setLevel(logging.INFO)

stream = logging.StreamHandler()
stream.setFormatter(EtherFormatter())
log.addHandler(stream)
werkzeug.addHandler(stream)

file = logging.FileHandler("logs.log")

log.addHandler(file)
