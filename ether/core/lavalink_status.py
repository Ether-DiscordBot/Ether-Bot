import socket
import time

from ether.core.config import config
from ether.core.logging import log


def lavalink_request(timeout=10.0):
    log.info("Checking lavalink socket status...")
    start_time = time.perf_counter()
    while not config.lavalink.get("https"):
        try:
            with socket.create_connection(
                (config.lavalink.get("host", config.lavalink.get("port"))),
                timeout=timeout,
            ):
                break
        except OSError as _e:
            time.sleep(0.01)
            if time.perf_counter() - start_time >= timeout:
                log.warning("Lavalink socket is not open")
                return None

    log.info("Lavalink socket is open")
    return 0
