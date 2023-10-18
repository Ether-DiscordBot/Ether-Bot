import socket
import time

from ether.core.config import config
from ether.core.logging import log


def lavalink_request(timeout=10.0, in_container: bool = False):
    log.info("Checking lavalink socket status...")
    start_time = time.perf_counter()
    config_node = config.lavalink.get("default_node")

    while True:
        if config_node.get("secure"):
            break
        try:
            with socket.create_connection(
                # If is in docker: host = lavalink
                (
                    "lavalink" if in_container else config_node.get("host"),
                    config_node.get("port"),
                ),
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
