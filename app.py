import discord
from discord.ext import commands
from discord.ext.commands.errors import (
    MissingPermissions,
    UserNotFound,
    CommandNotFound,
    CommandOnCooldown,
    MissingRequiredArgument,
)
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice
from discord import Embed
import os
from dotenv import load_dotenv
import random

from core import LoaderManager

from core import Colour
from core import MusicCommandsManager
from core import RedditCommandsManager
from core import Database

load_dotenv()


class App:
    APP_VERSION = "0.0.5dev1"

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
            prefix=os.getenv("BASE_PREFIX"),
            token=os.getenv("BOT_TOKEN"),
        )

        client.run(client.token)


class Client(commands.Bot):
    def __init__(self, prefix=None, token=None):
        self.prefix = prefix
        self.token = token
        self.bot_link = "https://discord.com/oauth2/authorize?client_id=693456698299383829&permissions=3757567862&scope=bot%20applications.commands"

        self._loader = LoaderManager(self)
        self.db = None
        self.musicCmd = None
        self.redditCmd = None

        super().__init__(
            intents=discord.Intents.all(), command_prefix=self.prefix, help_command=None
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

        self.musicCmd = MusicCommandsManager(self)
        await self.musicCmd.init()

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
        if member.id != self.id:
            guild = self.db.get_guild(member.guild)
            log = guild["logs"]["leave"]
            if log["active"]:
                channel = member.guild.get_channel(log["channel_id"])
                if channel:
                    await channel.send(
                        log["message"].format(user=member, guild=member.guild)
                    )

    async def on_message(self, ctx):
        db_guild = self.db.get_guild(ctx.guild)
        self.db.get_user(ctx.author, ctx.guild)
        if not ctx.author.bot:
            random.seed()
            if random.randint(1, 100) <= 37:
                self.db.add_exp(ctx.author, ctx.guild, 5)

            await self.process_commands(ctx)

    async def on_command_error(self, ctx, error):
        ignored = (commands.NoPrivateMessage, commands.DisabledCommand, commands.CheckFailure,
                   commands.CommandNotFound, commands.UserInputError, discord.HTTPException)
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return
