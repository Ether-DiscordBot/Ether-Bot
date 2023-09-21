import asyncio
import os
import sys
import signal

import discord
import mafic
import nest_asyncio
from discord.ext import commands

from ether import __version__
from ether.core.lavalink_status import lavalink_request
from ether.core.logging import log

nest_asyncio.apply()

from ether.core.cog_manager import CogManager
from ether.core.config import config
from ether.core.db import init_database
from ether.api.server import ServerThread

init_database(config.database.mongodb.get("uri"))

threads = []


#
#               Ether - Discord Bot
#
#              Made by  Atomic Junky
#


class Client(commands.Bot):
    def __init__(self):
        self.in_container: bool = os.environ.get("IN_DOCKER", False)
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

    async def start_lavalink_node(self):
        if config.lavalink.get("https"):
            r = lavalink_request(timeout=20.0, in_container=self.in_container)
        else:
            r = 0

        if r != 0:
            await self.remove_cog("cogs.music")
        elif not self.lavalink_ready_ran:
            node = await self.pool.create_node(
                host=config.lavalink.get("host"),
                port=config.lavalink.get("port"),
                label="MAIN",
                password=config.lavalink.get("pass"),
                secure=config.lavalink.get("https"),
            )
            self.lavalink_ready_ran = True

            log.info("Lavalink node created")
            log.info(f"\tNode {node.label}: {node.host}:{node.port}")
            if not hasattr(node, "session"):
                log.warning(f"Node ({node.label}) session is empty")

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
