import random
import os
import asyncio

import discord
from discord.ext import commands
import nest_asyncio

nest_asyncio.apply()

from ether.core.cog_manager import CogManager
from ether.core.db import Database, Guild, GuildUser, init_database
from ether.core.logging import log
from ether.core.lavalink_status import request
from ether.core.config import config

init_database(config.database.mongodb.get("uri"))


#
#               Ether - Discord Bot
#
#              Made by Holy Crusader
#


class Client(commands.Bot):
    def __init__(self):
        self.in_container: bool = os.environ.get("IN_DOCKER", False)
        self.lavalink_host = "lavalink" if self.in_container else "localhost"

        intents = discord.Intents().all()
        
        self.debug_guilds: list[int] = list(config.bot.get("debugGuilds"))
        if config.bot.get("global"):
            self.debug_guilds = None          

        super().__init__(
            activity=discord.Game(name="/help"),
            help_command=None,
            debug_guilds=self.debug_guilds,
            intents=intents,
        )

    async def load_extensions(self):
        await CogManager.load_cogs(self)

    async def on_ready(self):
        log.info(f"Client Name:\t{self.user.name}")
        log.info(f"Client ID:\t{self.user.id}")
        log.info(f"Client Disc:\t{self.user.discriminator}")

        log.info(f"Is in container: {self.in_container}")

        gsc = config.bot.get("global")
        log.info(f"Global slash commands: {gsc}")
        
        opt = (self.lavalink_host, config.lavalink.get("port"))
        r = request(opt)
        if r != 0:
            await self.remove_cog(f'cogs.music')

        self.musicCmd = self.get_cog("music")

    async def on_member_join(self, member):
        guild = await Database.Guild.get_or_create(member.guild.id)

        if guild.logs and guild.logs.join and guild.logs.join.enabled:
            channel = member.guild.get_channel(guild.logs.join.channel_id)
            await channel.send(
                guild.logs.join.message.format(user=member, guild=member.guild)
            )

    async def on_member_remove(self, member):
        guild = await Database.Guild.get_or_create(member.guild.id)

        if guild.logs and guild.logs.leave and guild.logs.leave.enabled:
            channel = member.guild.get_channel(guild.logs.leave.channel_id)
            await channel.send(
                guild.logs.leave.message.format(user=member, guild=member.guild)
            )

    async def on_message(self, ctx):
        if ctx.author.bot:
            return

        if Database.client != None:
            await Guild.from_guild_object(ctx.guild)
            await GuildUser.from_member_object(ctx.author)
            if random.randint(1, 100) <= 33:
                new_level = await Database.GuildUser.add_exp(
                    ctx.author.id, ctx.guild.id, 4
                )
                if new_level:
                    await ctx.channel.send(
                        f"Congratulation <@{ctx.author.id}>, you just pass to level {new_level}!"
                    )

        await self.process_commands(ctx)
    
    
    async def remove_cog(ctx, extension):
        log.info(f"Removed cog: {extension}")

    async def on_command_error(self, ctx, error):
        ignored = (
            commands.NoPrivateMessage,
            commands.DisabledCommand,
            commands.CheckFailure,
            commands.CommandNotFound,
            commands.UserInputError,
            discord.HTTPException,
            discord.errors.NotFound,
        )
        error = getattr(error, "original", error)

        if isinstance(error, ignored):
            return

        raise error


def main():
    bot = Client()

    asyncio.run(bot.load_extensions())
    bot.run(config.bot.get("token"))


if __name__ == "__main__":
    main()
