import asyncio
import os
import threading

import discord
import nest_asyncio
from discord.ext import commands

nest_asyncio.apply()

from ether.core.cog_manager import CogManager
from ether.core.config import config
from ether.core.db import init_database
from ether.api.server import start as start_server

init_database(config.database.mongodb.get("uri"))


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


def main():
    bot = Client()

    server_thread = threading.Thread(
        target=start_server, kwargs={"port": config.server.get("port"), "bot": bot}
    )
    server_thread.start()

    asyncio.run(bot.load_extensions())

    bot.run(config.bot.get("token"))


if __name__ == "__main__":

    main()
