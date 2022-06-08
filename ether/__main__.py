import random
import os
import json
import asyncio

import discord
from discord.ext import commands
from dotenv import load_dotenv
import nest_asyncio
nest_asyncio.apply()

from ether.core.cog_manager import CogManager
from ether.core.db import Database
from ether.core.db.models import Guild, GuildUser
from ether.core.logging import log


#
#               Ether - Discord Bot
#
#              Made by Holy Crusader
#


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
            command_prefix=base_prefix,
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
        guild = await Database.Guild.get_or_create(member.guild.id)

        if guild.logs and guild.logs.join:
            if guild.logs.join.enabled:
                channel = member.guild.get_channel(guild.logs.join.channel_id)
                await channel.send(
                    guild.logs.join.message.format(user=member, guild=member.guild)
                )

    async def on_member_remove(self, member):
        guild = await Database.Guild.get_or_create(member.guild.id)
        
        if guild.logs and guild.logs.leave:
            if guild.logs.leave.enabled:
                channel = member.guild.get_channel(guild.logs.leave.channel_id)
                await channel.send(
                    guild.logs.leave.message.format(user=member, guild=member.guild)
                )

    async def on_message(self, ctx):
        if ctx.author.bot:
            return
    
        if Database.client != None:
            await Guild.from_guild_object(ctx.guild)
            await GuildUser.from_user_object(ctx.author)
            if random.randint(1, 100) <= 33:
                new_level = await Database.GuildUser.add_exp(ctx.author.id, ctx.guild.id, 4)
                if new_level:
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
