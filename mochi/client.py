from mochi.core import *
import discord
from discord.ext import commands as cmds
from discord.ext.commands.errors import (
    MissingPermissions,
    UserNotFound,
    CommandNotFound,
    CommandOnCooldown,
    MissingRequiredArgument,
)
from discord.ext.commands import when_mentioned_or
from discord import Embed
import os
from dotenv import load_dotenv
import random

from mochi.core import *

load_dotenv()

def get_prefix(client, message):
    guild = client.db.get_guild(message.guild)
    return when_mentioned_or(os.getenv("BASE_PREFIX"))(client, message) + guild['prefix']


class App:
    APP_VERSION = "0.0.5dev2"

    def run():
        print(
            "\033[34m \n\n __  __               _      _            _____   _                            _  ____    "
            "      _   \n"
            "|  \/  |             | |    (_)          |  __ \ (_)                          | ||  _ \        | | \n"
            "| \  / |  ___    ___ | |__   _   ______  | |  | | _  ___   ___  ___   _ __  __| || |_) |  ___  | |_ \n"
            "| |\/| | / _ \  / __|| '_ \ | | |______| | |  | || |/ __| / __|/ _ \ | '__|/ _` ||  _ <  / _ \ | __|\n"
            "| |  | || (_) || (__ | | | || |          | |__| || |\__ \| (__| (_) || |  | (_| || |_) || (_) || |_ \n"
            "|_|  |_| \___/  \___||_| |_||_|          |_____/ |_||___/ \___|\___/ |_|   \__,_||____/  \___/  "
            "\__|\n\033[37m"
        )
        print(f"\tVersion:\t{App.APP_VERSION}\n")

        client = Client(
            prefix=get_prefix,
            token=os.getenv("BOT_TOKEN"),
        )

        client.run(client.token)


class Client(cmds.Bot):
    def __init__(self, prefix=None, token=None):
        self.prefix = prefix
        self.token = token
        self.bot_link = "https://discord.com/oauth2/authorize?client_id=693456698299383829&permissions=3757567862&scope=bot%20applications.commands"

        self._loader = LoaderManager(self)
        self.db = None
        self.musicCmd = None
        self.redditCmd = None

        self.utils = Utils

        super().__init__(
            command_prefix=self.prefix, help_command=None
        )

    async def load_extensions(self):
        await self._loader.find_extension()

    async def on_ready(self):
        print(f"\tClient Name:\t{self.user.name}")
        print(f"\tClient ID:\t{self.user.id}")
        print(f"\tClient Disc:\t{self.user.discriminator}\n")

        await self.load_extensions()

        self.redditCmd = RedditCommandsManager(
            self,
            os.getenv("REDDIT_CLIENT_ID"),
            os.getenv("REDDIT_CLIENT_SECRET"),
            os.getenv("REDDIT_NAME"),
            os.getenv("REDDIT_PASS"),
        )

        self.musicCmd = await self.get_cog('music').start_nodes()

        self.db = Database()

    async def on_member_join(self, member):
        guild = self.db.get_guild(member.guild)
        log = guild["logs"]["join"]
        if log["active"]:
            channel = member.guild.get_channel(log["channel_id"])
            if channel:
                await channel.send(
                    log["message"].format(user=member, guild=member.guild)
                )

    async def on_member_remove(self, member):
        if member.id != self.user.id:
            guild = self.db.get_guild(member.guild)
            log = guild["logs"]["leave"]
            if log["active"]:
                channel = member.guild.get_channel(log["channel_id"])
                if channel:
                    await channel.send(
                        log["message"].format(user=member, guild=member.guild)
                    )

    async def on_message(self, ctx):
        self.db.get_guild(ctx.guild)
        self.db.get_user(ctx.guild, ctx.author)
        if not ctx.author.bot:
            random.seed()
            if random.randint(1, 100) <= 37:
                self.db.update_user(ctx.guild, ctx.author, "exp", 5)

            await self.process_commands(ctx)

    async def on_command_error(self, ctx, error):
        ignored = (cmds.NoPrivateMessage, cmds.DisabledCommand, cmds.CheckFailure,
                   cmds.CommandNotFound, cmds.UserInputError, discord.HTTPException)
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return
        
        raise error
