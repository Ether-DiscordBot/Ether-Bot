from discord.ext import commands
from discord.ext.commands import CommandNotFound, CommandOnCooldown, MissingRequiredArgument
from discord import Embed

import os
import asyncio
from dotenv import load_dotenv

from core.music import MusicCommandsManager
from core.reddit import RedditCommandsManager

load_dotenv()


class Client(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=os.getenv("BASE_PREFIX"))
        self.musicCmd = MusicCommandsManager(self)
        self.redditCmd = RedditCommandsManager()

    async def on_ready(self):
        os.system("cls")
        print(
            "\033[34m \n\n\n __  __               _      _            _____   _                            _  ____    "
            "      _   \n"
            "|  \/  |             | |    (_)          |  __ \ (_)                          | ||  _ \        | | \n"
            "| \  / |  ___    ___ | |__   _   ______  | |  | | _  ___   ___  ___   _ __  __| || |_) |  ___  | |_ \n"
            "| |\/| | / _ \  / __|| '_ \ | | |______| | |  | || |/ __| / __|/ _ \ | '__|/ _` ||  _ <  / _ \ | __|\n"
            "| |  | || (_) || (__ | | | || |          | |__| || |\__ \| (__| (_) || |  | (_| || |_) || (_) || |_ \n"
            "|_|  |_| \___/  \___||_| |_||_|          |_____/ |_||___/ \___|\___/ |_|   \__,_||____/  \___/  "
            "\__|\n\n\n\033[37m")

        print("Logges as {0.display_name}#{0.discriminator} !".format(self.user))

        for file in os.listdir("cogs"):
            if file.endswith(".py"):
                name = file[:-3]
                self.load_extension(f"cogs.{name}")
                print(f"--- Commands loaded: {name}")

        await self.musicCmd.init()

    async def on_command_error(self, ctx, error):
        if isinstance(error, CommandNotFound):
            return
        elif isinstance(error, CommandOnCooldown):
            time_left = str(error)[34:]
            error_msg = await ctx.send(
                embed=Embed(description=f"You are on cooldown for this command.\nPlease try again in **{time_left}**",
                            color=0xe74c3c))
            await asyncio.sleep(2)
            await error_msg.delete()
            return
        elif isinstance(error, MissingRequiredArgument):
            return
        raise error
