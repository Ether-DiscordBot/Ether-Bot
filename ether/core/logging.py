import logging

LOG_FORMAT = "[%(levelname)s] %(asctime)s \t: %(message)s"
logging.basicConfig(
    filename="debug.log", level=logging.DEBUG, format=LOG_FORMAT, filemode="w"
)

log = logging.getLogger("ether_log")

stream = logging.StreamHandler()
stream.setLevel(logging.DEBUG)
stream.setFormatter(logging.Formatter(LOG_FORMAT))

log.addHandler(stream)