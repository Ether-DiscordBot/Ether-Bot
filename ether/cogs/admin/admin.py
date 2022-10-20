from typing import Optional

import discord
from discord import Embed, Member, Option, SlashCommandGroup, TextChannel, User
from humanize import precisedelta

from discord.ext import commands
from ether.core.constants import Colors
from ether.core.db.client import Database, Guild, Logs, JoinLog, LeaveLog, ModerationLog
from ether.core.logs import EtherLogs
from ether.core.utils import EtherEmbeds
from ether.core.constants import Emoji
from pycord18n.extension import _


class Admin(commands.Cog, name="admin"):
    def __init__(self, client):
        self.help_icon = Emoji.ADMIN
        self.client = client

    admin = SlashCommandGroup("admin", "Admin commands!")

    config = admin.create_subgroup("config", "Configuration commands!")

    @config.command(name="welcome")
    @commands.has_permissions(manage_guild=True)
    async def welcome(
        self,
        ctx: commands.Context,
        channel: Optional[TextChannel] = None,
        enabled: Optional[bool] = True,
    ):
        """Set the welcome channel"""
        guild = await Database.Guild.get_or_create(ctx.guild.id)

        channel = channel or ctx.channel
        await guild.set(
            {
                Guild.logs: Logs(
                    join=JoinLog(channel_id=channel.id, enabled=enabled),
                    leave=guild.logs.leave,
                    moderation=guild.logs.moderation,
                ).dict()
            }
        )
        if enabled == False:
            return await ctx.respond(
                embed=Embed(description=f"Welcome channel disabled")
            )
        return await ctx.respond(
            embed=Embed(description=f"Welcome channel set to <#{channel.id}>")
        )

    @config.command(name="leave")
    @commands.has_permissions(manage_guild=True)
    async def leave(
        self,
        ctx: commands.Context,
        channel: Optional[TextChannel] = None,
        enabled: Optional[bool] = True,
    ):
        """Set the leave channel"""
        guild = await Database.Guild.get_or_create(ctx.guild.id)

        channel = channel or ctx.channel
        await guild.set(
            {
                Guild.logs: Logs(
                    leave=LeaveLog(channel_id=channel.id, enabled=enabled),
                    join=guild.logs.join,
                    moderation=guild.logs.moderation,
                ).dict()
            }
        )

        if enabled == False:
            return await ctx.respond(embed=Embed(description="Leave channel disabled"))
        return await ctx.respond(
            embed=Embed(description=f"Leave channel set to <#{channel.id}>")
        )

    @config.command(name="log")
    @commands.has_permissions(manage_guild=True)
    async def log(
        self,
        ctx: commands.Context,
        channel: Optional[TextChannel] = None,
        enabled: Optional[bool] = True,
    ):
        """Set the log channel"""
        guild = await Database.Guild.get_or_create(ctx.guild.id)

        channel = channel or ctx.channel
        await guild.set(
            {
                Guild.logs: Logs(
                    moderation=ModerationLog(channel_id=channel.id, enabled=enabled),
                    join=guild.logs.join,
                    leave=guild.logs.leave,
                ).dict()
            }
        )

        if enabled == False:
            return await ctx.respond(embed=Embed(description="Log channel disabled"))
        return await ctx.respond(
            embed=Embed(description=f"Log channel set to <#{channel.id}>")
        )

    @admin.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: User, reason: str = None):
        """Ban a member"""
        guild = await Database.Guild.get_or_none(ctx.guild_id)

        if not guild:
            ctx.respond(
                embed=EtherEmbeds.error("Sorry, an unexpected error has occurred!"),
                delete_after=5,
            )

        # TODO replace try/except by a condition to check permissions

        try:
            await ctx.guild.ban(member)
            if guild.logs and guild.logs.moderation and guild.logs.moderation.enabled:
                if channel := ctx.guild.get_channel(guild.logs.moderation.channel_id):
                    await channel.send(
                        embed=EtherLogs.ban(
                            member, ctx.author.id, ctx.channel.id, reason
                        )
                    )

            return await ctx.respond("✅ Done")
        except discord.errors.Forbidden:
            await ctx.respond(
                embed=EtherEmbeds.error(
                    "Can't do that. Probably because I don't have the permissions for."
                )
            )

    @admin.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: Member, reason=None):
        """Kick a member"""
        guild = await Database.Guild.get_or_none(ctx.guild_id)

        if not guild:
            ctx.respond(
                embed=EtherEmbeds.error("Sorry, an unexpected error has occurred!"),
                delete_after=5,
            )

        # TODO replace try/except by a condition to check permissions

        try:
            await ctx.guild.kick(member)
            if guild.logs and guild.logs.moderation and guild.logs.moderation.enabled:
                if channel := ctx.guild.get_channel(guild.logs.moderation.channel_id):
                    await channel.send(
                        embed=EtherLogs.kick(
                            member, ctx.author.id, ctx.channel.id, reason
                        )
                    )

            return await ctx.respond("✅ Done")
        except discord.errors.Forbidden:
            await ctx.respond(
                embed=EtherEmbeds.error(
                    "Can't do that. Probably because I don't have the permissions for."
                )
            )

    @admin.command(name="clear")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        """Clear a specific amount of messages"""
        deleted = await ctx.channel.purge(limit=amount + 1)
        embed = Embed(description=f"Deleted {len(deleted) - 1} message(s).")
        embed.colour = Colors.SUCCESS
        await ctx.respond(embed=embed, delete_after=5)

    @admin.command(name="slowmode")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, cooldown: int):
        """Set the slowmode of the channel"""
        await ctx.channel.edit(slowmode_delay=cooldown)
        if cooldown == 0:
            await ctx.respond("✅ Slowmode disabled!")
            return
        await ctx.respond(f"✅ Slowmode set to `{precisedelta(cooldown)}`!")
