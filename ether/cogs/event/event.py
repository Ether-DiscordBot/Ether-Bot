import os
import random

from discord import ApplicationContext, Embed, File, HTTPException, errors
from discord.ext import commands
from ether.cogs.event.welcomecard import WelcomeCard

from ether.core.db.client import Database, Guild, GuildUser
from ether.core.lavalink_status import lavalink_request
from ether.core.logging import log
from ether.core.i18n import init_i18n
from ether.core.config import config


class Event(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.set_activity()
        in_container = os.environ.get("IN_DOCKER", False)

        log.info(f"Client Name: \t{self.client.user.name}")
        log.info(f"Client ID: \t{self.client.user.id}")
        log.info(f"Client Disc: \t{self.client.user.discriminator}")
        log.info(f"Guild Count: \t{len(self.client.guilds)}")

        log.info(f"Is in container: \t{in_container}")

        log.info("Global slash commands: {0}".format(config.bot.get("global")))

        r = lavalink_request(timeout=20.0, in_container=in_container)
        if r != 0:
            await self.client.remove_cog("cogs.music")

        init_i18n(self.client)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = await Database.Guild.get_or_create(member.guild.id)

        if guild.logs and guild.logs.join and guild.logs.join.enabled:
            channel = member.guild.get_channel(guild.logs.join.channel_id)
            if guild.logs.join.image:
                card = WelcomeCard.create_card(member, member.guild)
                return await channel.send(
                    file=File(fp=card, filename=f"welcome_{member.name}.png")
                )
            await channel.send(
                guild.logs.join.message.format(user=member, guild=member.guild)
            )

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = await Database.Guild.get_or_create(member.guild.id)

        if guild.logs and guild.logs.leave and guild.logs.leave.enabled:
            channel = member.guild.get_channel(guild.logs.leave.channel_id)
            await channel.send(
                guild.logs.leave.message.format(user=member, guild=member.guild)
            )

    @commands.Cog.listener()
    async def on_guild_join(self, _guild):
        await self.client.set_activity()

    @commands.Cog.listener()
    async def on_guild_remove(self, _guild):
        await self.client.set_activity()

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author.bot:
            return

        if Database.client != None:
            guild = await Guild.from_guild_object(ctx.guild)
            await GuildUser.from_member_object(ctx.author)
            if random.randint(1, 100) <= 33:
                new_level = await Database.GuildUser.add_exp(
                    ctx.author.id, ctx.guild.id, 4 * guild.exp_mult
                )
                if new_level:
                    await ctx.channel.send(
                        f"Congratulation <@{ctx.author.id}>, you just pass to level {new_level}!"
                    )

    @commands.Cog.listener()
    async def on_application_command(self, ctx):
        if random.randint(1, 100) <= 5:
            await ctx.channel.send(
                embed=Embed(
                    title="Support us!",
                    description="Ether is a free and open source bot, if you like it, please vote for the bot on [Top.gg](https://top.gg/bot/985100792270819389) and consider supporting us on [Ko-fi](https://ko-fi.com/holycrusader)!",
                    color=0x2F3136,
                )
            )

    @commands.Cog.listener()
    async def remove_cog(self, ctx: ApplicationContext, extension):
        log.info(f"Removed cog: {extension}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx: ApplicationContext, error):
        ignored = (
            commands.NoPrivateMessage,
            commands.DisabledCommand,
            commands.CheckFailure,
            commands.CommandNotFound,
            commands.UserInputError,
            HTTPException,
            errors.NotFound,
        )
        error = getattr(error, "original", error)

        if isinstance(error, ignored):
            return

        raise error
