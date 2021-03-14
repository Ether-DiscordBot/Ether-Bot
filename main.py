import asyncio
import os
import socket

from dotenv import load_dotenv

from discord.ext import commands
from discord.ext.commands import CommandNotFound, CommandOnCooldown
from discord import Embed

import lavalink

load_dotenv()

BASE_PREFIX = os.getenv('BASE_PREFIX')
TOKEN = os.getenv('BOT_TOKEN')

LAVALINK_HOST = os.getenv('LAVALINK_HOST')
LAVALINK_PORT = os.getenv('LAVALINK_PORT')
LAVALINK_PASS = os.getenv('LAVALINK_PASS')


class MochiBot(commands.Bot):
    def __init__(self) -> object:
        super().__init__(command_prefix=BASE_PREFIX)

    # When the bot is ready
    async def on_ready(self):
        print("Logges as {0.display_name}#{0.discriminator} !".format(self.user))

        # Start Lavalink
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            if s.connect_ex((LAVALINK_HOST, int(LAVALINK_PORT))) != 0: # Check if lavalink is already open
                lvlk = os.system("start cmd.exe /c java -jar Lavalink.jar") # Run Lavalink.jar in another command prompt

                if lvlk == 0:
                    print("--- Lavalink.jar is starting in a new command prompt !\n")

            else:
                print("--- Lavalink is already connected !\n")

        # Load commands
        for file in os.listdir("cogs"):
            if file.endswith(".py"):
                name = file[:-3]
                mochi_bot.load_extension(f"cogs.{name}")
                print(f"--- Commands loaded: {name}")

        # Init Lavalink client
        await lavalink.close()
        a = await lavalink.initialize(
            self, host=LAVALINK_HOST, password=LAVALINK_PASS,
            rest_port=LAVALINK_PORT, ws_port=LAVALINK_PORT
        )

        return print('--- Lavalink client as been initialized !')

    # When a command doesn't exist
    async def on_command_error(self, ctx, error):
        if isinstance(error, CommandNotFound):
            return
        elif isinstance(error, CommandOnCooldown):
            time_left = str(error)[34:]
            error_msg = await ctx.send(embed=Embed(description=f"You are on cooldown for this command.\nPlease try again in **{time_left}**", color=0xe74c3c))
            await asyncio.sleep(2)
            await error_msg.delete()
            return
        raise error



if __name__ == "__main__":
    mochi_bot = MochiBot()

mochi_bot.run(TOKEN)
