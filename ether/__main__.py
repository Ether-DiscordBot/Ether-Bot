import random
import os
import logging

import discord
from discord.ext import commands
from discord.ext.commands import when_mentioned_or
from dotenv import load_dotenv

from ether.core import Utils, CogManager, Database, EtherContext


LOG_FORMAT = "[%(levelname)s] %(asctime)s \t: %(message)s"
logging.basicConfig(
    filename="debug.log", level=logging.DEBUG, format=LOG_FORMAT, filemode="w"
)

logger = logging.getLogger("ether_log")

stream = logging.StreamHandler()
stream.setLevel(logging.DEBUG)
stream.setFormatter(logging.Formatter(LOG_FORMAT))

logger.addHandler(stream)


def get_prefix(client, message) -> str:
    prefix = client.db.get_guild(message.guild)["prefix"] or client.base_prefix
    return when_mentioned_or(prefix)(client, message)


class Client(commands.Bot):
    def __init__(self, base_prefix):
        self.base_prefix = base_prefix

        self.db = None
        self.musicCmd = None

        self.in_container: bool = os.environ.get("IN_DOCKER", False)

        self.utils = Utils

        self.lavalink_host = "lavalink" if self.in_container else "localhost"

        super().__init__(
            activity=discord.Game(name=f"{self.base_prefix}help"),
            command_prefix=get_prefix,
            help_command=None,
        )

    async def load_extensions(self):
        cogs_loader = CogManager(self)
        await cogs_loader.load_cogs()

    async def on_ready(self):
        logger.debug(f"Client Name:\t{self.user.name}")
        logger.debug(f"Client ID:\t{self.user.id}")
        logger.debug(f"Client Disc:\t{self.user.discriminator}")

        logger.debug(f"Is in container: {self.in_container}")

        await self.load_extensions()

        self.db = Database()

        self.musicCmd = self.get_cog("music")

    async def on_member_join(self, member):
        guild = self.db.get_guild(member.guild)
        log = guild["logs"]["join"]
        if log["active"]:
            if channel := member.guild.get_channel(log["channel_id"]):
                await channel.send(
                    log["message"].format(user=member, guild=member.guild)
                )

    async def on_member_remove(self, member):
        if member.id != self.user.id:
            guild = self.db.get_guild(member.guild)
            log = guild["logs"]["leave"]
            if log["active"]:
                if channel := member.guild.get_channel(log["channel_id"]):
                    await channel.send(
                        log["message"].format(user=member, guild=member.guild)
                    )

    async def get_context(self, message, *, cls=EtherContext):
        return await super().get_context(message, cls=cls)

    async def on_message(self, ctx):
        if ctx.author.bot:
            return

        if self.db:
            self.db.get_guild(ctx.guild)
            self.db.get_user(ctx.author)
            if random.randint(1, 100) <= 33:
                new_level = self.db.add_exp(ctx.guild, ctx.author, 4)
                if new_level != -1:
                    await ctx.channel.send(
                        f"Congratulation <@{ctx.author.id}>, you just pass to level {new_level}!"
                    )

        await self.process_commands(ctx)

    async def on_command_error(self, ctx, error):
        ignored = (
            commands.NoPrivateMessage,
            commands.DisabledCommand,
            commands.CheckFailure,
            commands.CommandNotFound,
            commands.UserInputError,
            discord.HTTPException,
        )
        error = getattr(error, "original", error)

        if isinstance(error, ignored):
            return

        raise error


def main():
    load_dotenv()

    bot = Client(base_prefix=os.getenv("BASE_PREFIX"))
    bot.run(os.getenv("BOT_TOKEN"))


if __name__ == "__main__":
    main()
