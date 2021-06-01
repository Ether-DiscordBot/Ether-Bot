from discord.ext import commands
from discord.ext.commands.errors import MissingPermissions, UserNotFound, CommandNotFound, CommandOnCooldown, \
    MissingRequiredArgument
from discord import Embed
import os
import asyncio
from dotenv import load_dotenv

import mochibot
from mochibot.core import LoaderManager
from mochibot.core import Colour
from mochibot.core import MusicCommandsManager
from mochibot.core import RedditCommandsManager

load_dotenv()


class Client(commands.Bot):
    def __init__(self, prefix=None, token=None):
        self.prefix = prefix
        self.token = token

        self._loader = LoaderManager(self)

        self.musicCmd = None
        self.redditCmd = None
        super().__init__(command_prefix=self.prefix)

    async def load_extensions(self):
        await self._loader.find_extension()

    async def on_ready(self):
        os.system("cls")
        print(
            "\033[34m \n\n __  __               _      _            _____   _                            _  ____    "
            "      _   \n"
            "|  \/  |             | |    (_)          |  __ \ (_)                          | ||  _ \        | | \n"
            "| \  / |  ___    ___ | |__   _   ______  | |  | | _  ___   ___  ___   _ __  __| || |_) |  ___  | |_ \n"
            "| |\/| | / _ \  / __|| '_ \ | | |______| | |  | || |/ __| / __|/ _ \ | '__|/ _` ||  _ <  / _ \ | __|\n"
            "| |  | || (_) || (__ | | | || |          | |__| || |\__ \| (__| (_) || |  | (_| || |_) || (_) || |_ \n"
            "|_|  |_| \___/  \___||_| |_||_|          |_____/ |_||___/ \___|\___/ |_|   \__,_||____/  \___/  "
            "\__|\n\033[37m")

        print(f"\tVersion:\t{mochibot.__version__}")
        print(f"\tClient Name:\t{self.user.name}")
        print(f"\tClient ID:\t{self.user.id}")
        print(f"\tClient Disc:\t{self.user.discriminator}\n")

        await self.load_extensions()

        self.redditCmd = RedditCommandsManager(self,
                                               os.getenv('REDDIT_CLIENT_ID'),
                                               os.getenv('REDDIT_CLIENT_SECRET'),
                                               os.getenv('REDDIT_NAME'),
                                               os.getenv('REDDIT_PASS'))

        self.musicCmd = MusicCommandsManager(self)
        await self.musicCmd.init()

    async def on_command_error(self, ctx, error):
        if isinstance(error, CommandNotFound):
            return
        elif isinstance(error, CommandOnCooldown):
            time_left = str(error)[34:]
            error_msg = await ctx.send(
                embed=Embed(colour=Colour.ERROR, description=f"You are on cooldown for this command.\nPlease try "
                                                             f"again in **{time_left}**",
                            color=0xe74c3c))
            await asyncio.sleep(2)
            await error_msg.delete()
            return
        elif isinstance(error, MissingRequiredArgument):
            return
        elif isinstance(error, MissingPermissions):
            embed = Embed(colour=Colour.ERROR, description=f"You don't have the **permissions** to do that.")
            return await ctx.send(embed=embed)
        elif isinstance(error, UserNotFound):
            embed = Embed(colour=Colour.ERROR, description=f"**Unknown** member.")
            return await ctx.send(embed=embed)
        raise error
