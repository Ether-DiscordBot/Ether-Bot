from typing import Optional

import discord
from discord import Embed, Member, TextChannel, User, app_commands
from discord.ext.commands import Cog
from humanize import precisedelta

from ether.core.constants import Colors
from ether.core.db.client import Database, Guild, Logs, JoinLog, LeaveLog, ModerationLog
from ether.core.logs import EtherLogs
from ether.core.embed import Embed
from ether.core.constants import Emoji
from ether.core.i18n import _


class Admin(Cog, name="admin"):
    def __init__(self, client):
        self.help_icon = Emoji.ADMIN
        self.client = client

    admin = app_commands.Group(
        name="admin", description="Admin related commands", guild_only=True
    )
    config = app_commands.Group(
        parent=admin, name="config", description="Admin configuration related commands"
    )

    @admin.command(name="ban")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.checks.bot_has_permissions(ban_members=True)
    async def ban(
        self, interaction: discord.Interaction, member: User, reason: str = None
    ):
        """Ban a member"""
        guild = await Database.Guild.get_or_none(interaction.guild_id)

        if not guild:
            interaction.response.send_message(
                embed=Embed.error("Sorry, an unexpected error has occurred!"),
                delete_after=5,
            )

        try:
            await interaction.guild.ban(member)
            if guild.logs and guild.logs.moderation and guild.logs.moderation.enabled:
                if channel := interaction.guild.get_channel(
                    guild.logs.moderation.channel_id
                ):
                    await channel.send(
                        embed=EtherLogs.ban(
                            member,
                            interaction.message.author.id,
                            interaction.message.channel.id,
                            reason,
                        )
                    )

            return await interaction.response.send_message("✅ Done")
        except discord.errors.Forbidden:
            await interaction.response.send_message(
                embed=Embed.error(
                    "Can't do that. Probably because I don't have the permissions for."
                )
            )

    @admin.command(name="kick")
    @app_commands.checks.has_permissions(kick_members=True)
    @app_commands.checks.bot_has_permissions(kick_members=True)
    async def kick(
        self,
        interaction: discord.Interaction,
        member: Member,
        reason: Optional[str] = None,
    ):
        """Kick a member"""
        guild = await Database.Guild.get_or_none(interaction.guild_id)

        if not guild:
            interaction.response.send_message(
                embed=Embed.error("Sorry, an unexpected error has occurred!"),
                delete_after=5,
            )

        # TODO replace try/except by a condition to check permissions

        try:
            await interaction.guild.kick(member)
            if guild.logs and guild.logs.moderation and guild.logs.moderation.enabled:
                if channel := interaction.guild.get_channel(
                    guild.logs.moderation.channel_id
                ):
                    await channel.send(
                        embed=EtherLogs.kick(
                            member,
                            interaction.message.author.id,
                            interaction.message.channel.id,
                            reason,
                        )
                    )

            return await interaction.response.send_message("✅ Done")
        except discord.errors.Forbidden:
            await interaction.response.send_message(
                embed=Embed.error(
                    "Can't do that. Probably because I don't have the permissions for."
                )
            )

    @admin.command(name="clear")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.bot_has_permissions(manage_messages=True)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def clear(self, interaction: discord.Interaction, amount: int):
        """Clear a specific amount of messages"""
        deleted = await interaction.message.channel.purge(limit=amount + 1)
        embed = Embed(description=f"Deleted {len(deleted) - 1} message(s).")
        embed.colour = Colors.SUCCESS
        await interaction.response.send_message(embed=embed, delete_after=5)

    @admin.command(name="slowmode")
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.checks.bot_has_permissions(manage_channels=True)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def slowmode(self, interaction: discord.Interaction, cooldown: int):
        """Set the slowmode of the channel"""
        await interaction.message.channel.edit(slowmode_delay=cooldown)
        if cooldown == 0:
            await interaction.response.send_message("✅ Slowmode disabled!")
            return
        await interaction.response.send_message(
            f"✅ Slowmode set to `{precisedelta(cooldown)}`!"
        )

    @config.command(name="welcome")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def welcome(
        self,
        interaction: discord.Interaction,
        channel: Optional[TextChannel] = None,
        enabled: Optional[bool] = True,
        image: Optional[bool] = False,
    ):
        """Set the welcome channel"""
        guild = await Database.Guild.get_or_create(interaction.guild.id)

        channel = channel or interaction.message.channel
        await guild.set(
            {
                Guild.logs: Logs(
                    join=JoinLog(channel_id=channel.id, enabled=enabled, image=image),
                    leave=guild.logs.leave or None if guild.logs else None,
                    moderation=guild.logs.moderation or None if guild.logs else None,
                ).dict()
            }
        )
        if enabled == False:
            return await interaction.response.send_message(
                embed=Embed.success(description=f"Welcome channel disabled"),
                ephemeral=True,
                delete_after=5,
            )
        return await interaction.response.send_message(
            embed=Embed.success(description=f"Welcome channel set to <#{channel.id}>"),
            ephemeral=True,
            delete_after=5,
        )

    @config.command(name="leave")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def leave(
        self,
        interaction: discord.Interaction,
        channel: Optional[TextChannel] = None,
        enabled: Optional[bool] = True,
    ):
        """Set the leave channel"""
        guild = await Database.Guild.get_or_create(interaction.guild.id)

        channel = channel or interaction.message.channel
        await guild.set(
            {
                Guild.logs: Logs(
                    leave=LeaveLog(channel_id=channel.id, enabled=enabled),
                    join=guild.logs.join or None if guild.logs else None,
                    moderation=guild.logs.moderation or None if guild.logs else None,
                ).dict()
            }
        )

        if enabled == False:
            return await interaction.response.send_message(
                embed=Embed.success(description="Leave channel disabled"),
                ephemeral=True,
                delete_after=5,
            )
        return await interaction.response.send_message(
            embed=Embed.success(description=f"Leave channel set to <#{channel.id}>"),
            ephemeral=True,
            delete_after=5,
        )

    @config.command(name="log")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def log(
        self,
        interaction: discord.Interaction,
        channel: Optional[TextChannel] = None,
        enabled: Optional[bool] = True,
    ):
        """Set the log channel"""
        guild = await Database.Guild.get_or_create(interaction.guild.id)

        channel = channel or interaction.message.channel
        await guild.set(
            {
                Guild.logs: Logs(
                    moderation=ModerationLog(channel_id=channel.id, enabled=enabled),
                    join=guild.logs.join or None if guild.logs else None,
                    leave=guild.logs.leave or None if guild.logs else None,
                ).dict()
            }
        )

        if enabled == False:
            return await interaction.response.send_message(
                embed=Embed.success(description="Log channel disabled"),
                ephemeral=True,
                delete_after=5,
            )
        return await interaction.response.send_message(
            embed=Embed.success(description=f"Log channel set to <#{channel.id}>"),
            ephemeral=True,
            delete_after=5,
        )
