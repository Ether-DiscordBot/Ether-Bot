from discord import SlashCommandGroup

from ether.core.config import config


# protected decorator for recusrion functions with a max depth
def recursion(*args, **kwargs):
    max_depth = kwargs.get("max_depth", 10)

    def _trace(func):
        def wrapper(*args, **kwargs):
            if not hasattr(func, "__depth__"):
                setattr(func, "__depth__", 0)

            if func.__depth__ >= max_depth:
                print(f"Stop a too deep recursion function (max depth: {max_depth})")
                return

            func.__depth__ += 1
            return func(*args, **kwargs)

        return wrapper

    return _trace(args[0]) if len(args) == 1 and callable(args[0]) else _trace


class DBLClient:
    def __init__(self, client) -> None:
        self.client = client
        # self.dbl_api_key = config.api.dbl.get("key")

    def submit_command(self):
        """Submit a command to the bot list."""
        url = f"https://discordbotlist.com/api/v1/bots/{self.client.user.id}/commands"

        return

    def submit_stat(self):
        """Submit a stat to the bot list."""
        url = f"https://discordbotlist.com/api/v1/bots/{self.client.id}/stats"
