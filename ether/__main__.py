import random
import os
import json
import asyncio

import discord
from discord.ext import commands
from discord.ext.commands import when_mentioned_or
from dotenv import load_dotenv
import nest_asyncio

from ether.core.cog_manager import CogManager
from ether.core.context import EtherContext
from ether.core.db import Database
from ether.core.db.models import Guild, GuildUser, User
from ether.core.logging import log

nest_asyncio.apply()
bot = None


def get_prefix(client, message) -> str:
    prefix = client.base_prefix
    if Database.client:
        prefix = Database.get_guild(message.guild)["prefix"] or client.base_prefix
    return when_mentioned_or(prefix)(client, message)


class Client(commands.Bot):
    def __init__(self, base_prefix):
        self.base_prefix = base_prefix

        self.musicCmd = None

        self.in_container: bool = os.environ.get("IN_DOCKER", False)

        self.lavalink_host = "lavalink" if self.in_container else "localhost"

        guilds = json.loads(os.environ.get("SLASH_COMMANDS_GUILD_ID", default=[]))
        self.debug_guilds: list[int] = [g for g in guilds]
        intents = discord.Intents().all()

        super().__init__(
            activity=discord.Game(name=f"{self.base_prefix}help"),
            command_prefix=get_prefix,
            help_command=None,
            debug_guilds=[697735468875513876],
            intents=intents,
        )

    async def load_extensions(self):
        cogs_loader = CogManager(self)
        await cogs_loader.load_cogs()

    async def on_ready(self):
        log.info(f"Client Name:\t{self.user.name}")
        log.info(f"Client ID:\t{self.user.id}")
        log.info(f"Client Disc:\t{self.user.discriminator}")

        log.info(f"Is in container: {self.in_container}")

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
    
        if Database.client != None:
            await Guild.from_guild_object(ctx.guild)
            await GuildUser.from_user_object(ctx.author)
            if random.randint(1, 100) <= 33:
                new_level = Database.GuildUser.add_exp(ctx.guild, ctx.author, 4)
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
    
    asyncio.run(bot.load_extensions())
    bot.run(os.getenv("BOT_TOKEN"))


if __name__ == "__main__":
    main()
