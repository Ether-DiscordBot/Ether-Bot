import logging
import time

import socket

opt = ("lavalink", 2333)

logger = logging.getLogger("ether_log")


def request(timeout=5.0):
    logger.debug("Checking lavalink socket status...")
    start_time = time.perf_counter()
    while True:
        try:
            with socket.create_connection(opt, timeout=timeout):
                break
        except OSError as ex:
            time.sleep(0.01)
            if time.perf_counter() - start_time >= timeout:
                logger.error("Lavalink socket is not open")
                raise TimeoutError(
                    "Waited too long for the port {} on host {} to start accepting "
                    "connections.".format(opt[1], opt[0])
                ) from ex

    logger.debug("Lavalink socket is open")
    return 0
