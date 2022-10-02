from email.policy import default
from typing import Optional
from discord import Embed, Member, Option, Role, SlashCommandGroup, TextChannel, User, slash_command
import discord
from discord.ext import commands
from humanize import precisedelta

from ether.core.constants import Colors
from ether.core.db.client import Database
from ether.core.utils import EtherEmbeds
from ether.core.logs import EtherLogs


class Admin(commands.Cog, name="admin"):
    def __init__(self, client):
        self.help_icon = "🛡️"
        self.client = client

    admin = SlashCommandGroup("admin", "Admin commands!")

    @admin.command(name="warn")
    @commands.has_permissions(ban_members=True)
    async def warn(self, ctx, member: User, reason: str = None):
        # TODO Warn a member of the server
        pass

    @admin.command(name="mute")
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: User, time: Option(int, "Time in sec", min_value=1, default=-1), reason: str = None):
        # TODO Mute a member
        pass
    
    @admin.command(name="unmute")
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: User):
        # TODO Unmute a member
        pass
    
    @admin.command(name="captcha")
    @commands.has_permissions(administrator=True)
    async def captcha(self, ctx, role: Role, channel: TextChannel = None):
        # TODO Captcha verification
        pass

    @admin.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: User, reason: str = None):
        guild = await Database.Guild.get_or_none(ctx.guild_id)

        if not guild:
            ctx.respond(
                embed=EtherEmbeds.error("Sorry, an unexpected error has occurred!"),
                delete_after=5,
            )

        # TODO replace try/except by a condition to check permissions

        try:
            await ctx.guild.ban(member)
            if (
                guild.logs
                and guild.logs.moderation
                and guild.logs.moderation.enabled
            ):
                if channel := ctx.guild.get_channel(
                    guild.logs.moderation.channel_id
                ):
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
        guild = await Database.Guild.get_or_none(ctx.guild_id)

        if not guild:
            ctx.respond(
                embed=EtherEmbeds.error("Sorry, an unexpected error has occurred!"),
                delete_after=5,
            )

        # TODO replace try/except by a condition to check permissions

        try:
            await ctx.guild.kick(member)
            if (
                guild.logs
                and guild.logs.moderation
                and guild.logs.moderation.enabled
            ):
                if channel := ctx.guild.get_channel(
                    guild.logs.moderation.channel_id
                ):
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
        deleted = await ctx.channel.purge(limit=amount + 1)
        embed = Embed(description=f"Deleted {len(deleted) - 1} message(s).")
        embed.colour = Colors.SUCCESS
        await ctx.respond(embed=embed, delete_after=5)

    @admin.command(name="slowmode")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, cooldown: int):
        await ctx.channel.edit(slowmode_delay=cooldown)
        if cooldown == 0:
            await ctx.respond("✅ Slowmode disabled!")
            return
        await ctx.respond(f"✅ Slowmode set to `{precisedelta(cooldown)}`!")

    @admin.command(name="logs")
    @commands.has_permissions(manage_channels=True)
    async def logs(
        self, ctx, active: bool, channel: Optional[discord.TextChannel] = None
    ):

        if channel:
            res = await Database.Guild.Logs.Moderation.set(
                ctx.guild.id, active, channel.id
            )
        else:
            res = await Database.Guild.Logs.Moderation.set(ctx.guild.id, active)

        if not res:
            ctx.respond(
                embed=EtherEmbeds.error("Sorry, an unexpected error has occurred!"),
                delete_after=5,
            )

        if active:
            return await ctx.respond("✅ Logs set enabled!")

        return await ctx.respond("✅ Logs set disabled!")
