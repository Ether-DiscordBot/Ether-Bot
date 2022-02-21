from ether.core import *
import discord
from discord.ext import commands as cmds
from discord.ext.commands import when_mentioned_or
import os
from dotenv import load_dotenv
import random

from ether.core import *

load_dotenv()


def get_prefix(client, message):
    guild = client.db.get_guild(message.guild)
    return when_mentioned_or(os.getenv("BASE_PREFIX"))(client, message) + list(guild['prefix'])


APP_VERSION = "0.0.7dev3"


class Client(cmds.Bot):
    def __init__(self, prefix: str = None, in_container: bool = False):
        self.prefix = prefix

        self.db = None
        self.musicCmd = None
        self.redditCmd = None

        self.in_container = in_container

        self.utils = Utils

        self.lavalink_host = "lavalink" if self.in_container else "localhost"

        super().__init__(
            command_prefix=self.prefix, help_command=None
        )

    async def load_extensions(self):
        cogs_loader = CogManager(self)
        await cogs_loader.load_cogs()

    async def on_ready(self):
        print(f"\n\tClient Name:\t{self.user.name}")
        print(f"\tClient ID:\t{self.user.id}")
        print(f"\tClient Disc:\t{self.user.discriminator}\n")

        print(f"\t Is in container: {self.in_container}\n")

        await self.load_extensions()

        self.redditCmd = RedditCommandsManager(
            self,
            os.getenv("REDDIT_CLIENT_ID"),
            os.getenv("REDDIT_CLIENT_SECRET"),
            os.getenv("REDDIT_NAME"),
            os.getenv("REDDIT_PASS"),
        )

        self.db = Database()

        self.musicCmd = self.get_cog('music')

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

    async def on_message(self, ctx):
        if ctx.author.bot:
            return

        if self.db:
            self.db.get_guild(ctx.guild)
            self.db.get_user(ctx.author)
            if random.randint(1, 100) <= 33:
                new_level = self.db.add_exp(ctx.guild, ctx.author, 4)
                if new_level != -1:
                    await ctx.channel.send(f'Congratulation <@{ctx.author.id}>, you just pass to level {new_level}!')

        await self.process_commands(ctx)

    async def on_command_error(self, ctx, error):
        ignored = (cmds.NoPrivateMessage, cmds.DisabledCommand, cmds.CheckFailure,
                   cmds.CommandNotFound, cmds.UserInputError, discord.HTTPException)
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        raise error
