import asyncio
import random
import sys
import signal

import discord
import mafic
import nest_asyncio
from discord.ext import commands

nest_asyncio.apply()

from ether import __version__
from ether.core.config import config
from ether.core.constants import NODE_CODE_NAME
from ether.core.lavalink_status import lavalink_request
from ether.core.logging import log
from ether.core.voice_client import EtherPlayer
from ether.core.cog_manager import CogManager
from ether.core.db import init_database
from ether.api.server import ServerThread
from ether.core.botlist import DBLClient

init_database(config.database.mongodb.get("uri"))

threads = []
subprocesses = []


#
#               Ether - Discord Bot
#
#              Made by  Atomic Junky
#


class Client(commands.Bot):
    def __init__(self):
        # self.dbl = DBLClient(self)
        self.lavalink_ready_ran = False

        intents = discord.Intents().all()

        self.debug_guilds: list[int] = list(config.bot.get("debugGuilds"))
        if config.bot.get("global"):
            self.debug_guilds = None

        super().__init__(
            help_command=None,
            debug_guilds=self.debug_guilds,
            intents=intents,
        )

        self.pool = mafic.NodePool(self)

    async def start_lavalink_node(self, init: bool = False):
        lavalink_request()
        if config.lavalink.get("secure"):
            r = lavalink_request(timeout=20.0, in_container=self.in_container)
        else:
            r = 0

        if r != 0:
            await self.remove_cog("cogs.music")
        elif (not self.lavalink_ready_ran and init) or not init:
            log.info("Creating a new lavalink node...")

            config_node = config.lavalink.get("default_node")
            if not init and config.lavalink.get("nodes"):
                config_nodes = config.lavalink.get("nodes")

                for node in self.pool.nodes:
                    for config_node in config_nodes:

                        if not isinstance(config_node, dict):
                            log.warning(
                                f"Invalid type for the config node variable (type: {type(config_node)}):\n{config_node}"
                            )
                            continue

                        if node.host == config_node.get(
                            "host"
                        ) and node.port == config_node.get("port"):
                            config_nodes.remove(config_node)
                            continue

                if len(config_nodes) <= 0:
                    log.warning(
                        "All hosts are already used, switching to the default one"
                    )
                    config_node = config.lavalink.get("default_node")
                else:
                    config_node = random.choice(config_nodes)

            try:
                node = await self.pool.create_node(
                    host=config_node.get("host"),
                    port=config_node.get("port"),
                    label=NODE_CODE_NAME.get_random(),
                    password=config_node.get("pass"),
                    secure=config_node.get("secure"),
                    player_cls=EtherPlayer,
                )
                self.lavalink_ready_ran = True

                log.info(f"Node {node.label} created")
                log.info(f"\tHost: {node.host}:{node.port}")

                return node
            except Exception as e:
                log.error(
                    f"Failed to create a lavalink node ({config_node.host}:{config_node.port}): {e}"
                )

        return None

    async def set_activity(self):
        await self.change_presence(
            activity=discord.Game(name=f"/help | v{__version__}")
        )

    async def load_extensions(self):
        await CogManager.load_cogs(self)


def signal_handler(sig, frame):
    # Exit the program
    print("\033[35mProcess killed by user\033[0m")
    # Close the bot
    for thread in threads:
        thread.kill()
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, signal_handler)

    global bot
    bot = Client()

    server_thread = ServerThread(port=config.server.get("port"), bot=bot)
    threads.append(server_thread)
    server_thread.start()

    asyncio.run(bot.load_extensions())
    bot.run(config.bot.get("token"))


if __name__ == "__main__":
    main()
