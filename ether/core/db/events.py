from pymongo import monitoring

from ether.core.logging import db_log


class ServerLogger(monitoring.ServerListener):
    def opened(self, event):
        db_log.info(f"MongoDB server {event.server_address} added to topology {event.topology_id}")

    def description_changed(self, _event):
        return

    def closed(self, event):
        db_log.warning(f"MongoDB server {event.server_address} removed from topology {event.topology_id}")


monitoring.register(ServerLogger())
