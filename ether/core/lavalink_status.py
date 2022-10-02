import os
import time

import socket

from ether.core.logging import log


def request(opt, timeout=10.0):
    log.info("Checking lavalink socket status...")
    start_time = time.perf_counter()
    while True:
        try:
            with socket.create_connection(opt, timeout=timeout):
                break
        except OSError as _ex:
            time.sleep(0.01)
            if time.perf_counter() - start_time >= timeout:
                log.warning("Lavalink socket is not open")
                return None

    log.info("Lavalink socket is open")
    return 0
