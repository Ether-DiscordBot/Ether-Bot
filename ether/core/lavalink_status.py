import time

import socket

from ether.core.logging import log

opt = ("lavalink", 2333)


def request(timeout=5.0):
    log.info("Checking lavalink socket status...")
    start_time = time.perf_counter()
    while True:
        try:
            with socket.create_connection(opt, timeout=timeout):
                break
        except OSError as ex:
            time.sleep(0.01)
            if time.perf_counter() - start_time >= timeout:
                log.error("Lavalink socket is not open")
                raise TimeoutError(
                    "Waited too long for the port {} on host {} to start accepting "
                    "connections.".format(opt[1], opt[0])
                ) from ex

    log.info("Lavalink socket is open")
    return 0
