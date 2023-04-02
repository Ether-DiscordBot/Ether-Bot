import asyncio
import os
import sys
import signal

import discord
import nest_asyncio
from discord.ext import commands

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
#              Made by Holy Crusader
#


class Client(commands.Bot):
    def __init__(self):
        self.in_container: bool = os.environ.get("IN_DOCKER", False)

        intents = discord.Intents().all()

        self.debug_guilds: list[int] = list(config.bot.get("debugGuilds"))
        if config.bot.get("global"):
            self.debug_guilds = None

        super().__init__(
            help_command=None,
            debug_guilds=self.debug_guilds,
            intents=intents,
        )

    async def set_activity(self):
        await self.change_presence(
            activity=discord.Game(name=f"/help | On {len(self.guilds)} servers")
        )

    async def load_extensions(self):
        await CogManager.load_cogs(self)

    def booba(self):
        return self.user.name


def signal_handler(sig, frame):
    # Exit the program
    print("\033[35mProcess killed by user\033[0m")
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
