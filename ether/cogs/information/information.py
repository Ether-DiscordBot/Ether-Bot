from typing import Optional

import discord
from discord import Member, app_commands
from discord.ext import commands
from discord.ext.commands import Context
from humanize import naturaldate, naturalsize

from ether.core.constants import Emoji
from ether.core.embed import Embed, ErrorEmbed
from ether.core.i18n import _


class InformationHandler:
    @classmethod
    def get_user_infos(cls, user) -> Embed:
        avatar = user.avatar.url if user.avatar else user.default_avatar.url

        embed = Embed(description=f"**ID:** {user.id}")
        embed.set_author(
            name=f"{user.name}#{user.discriminator}", icon_url=avatar, url=avatar
        )

        embed.set_thumbnail(url=avatar)
        embed.add_field(
            name="Account creation date",
            value=naturaldate(user.created_at),
            inline=False,
        )

        embed.add_field(
            name="Server join date",
            value=naturaldate(user.joined_at),
            inline=False,
        )

        return embed

    @classmethod
    def get_user_avatar(cls, user) -> Embed:
        avatar = user.avatar.url if user.avatar else user.default_avatar.url

        return Embed(
            description=f"**{user.display_name}'s** [avatar]({avatar}):"
        ).set_image(url=avatar)


class Information(commands.GroupCog, name="information"):
    def __init__(self, client):
        self.help_icon = Emoji.INFORMATION
        self.client = client

        self.user_infos_menu = app_commands.ContextMenu(
            name="User infos",
            callback=self.user_infos,
        )
        self.client.tree.add_command(self.user_infos_menu)

        self.user_avatar_menu = app_commands.ContextMenu(
            name="User avatar",
            callback=self.user_avatar,
        )
        self.client.tree.add_command(self.user_avatar_menu)

    @app_commands.command(name="user")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def user(self, interaction: discord.Interaction, member: Member = None):
        """Get information about a user"""
        member = member or interaction.user
        await interaction.response.send_message(
            embed=InformationHandler.get_user_infos(member)
        )

    @app_commands.command(name="server")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def server(self, interaction: discord.Interaction):
        """Get information about the server"""
        guild = interaction.guild

        embed = Embed(title="", description=f"**ID:** {guild.id}")
        embed.set_thumbnail(url=guild.icon)
        embed.add_field(name="Server boost", value=f"Level {guild.premium_tier}/3")
        embed.add_field(
            name="Members",
            value=f"{guild.member_count}/{guild.max_members}",
            inline=False,
        )
        embed.add_field(
            name="Server creation date",
            value=naturaldate(guild.created_at),
            inline=False,
        )
        embed.add_field(
            name="Additional information",
            value=f"\t**Emoji:** {len(guild.emojis)}/{guild.emoji_limit}\n"
            f"\t**Sticker:** {len(guild.stickers)}/{guild.sticker_limit}\n"
            f"\t**Filesize:** {naturalsize(guild.filesize_limit, binary=True)}",
            inline=False,
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="avatar")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def avatar(
        self, interaction: discord.Interaction, member: Optional[Member] = None
    ):
        """Get the avatar of a user"""
        user = member or interaction.user
        return await interaction.response.send_message(
            embed=InformationHandler.get_user_avatar(user)
        )

    # Context Menu

    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def user_infos(self, interaction: discord.Interaction, user: Member):
        """Get information about a user"""
        return await interaction.response.send_message(
            embed=InformationHandler.get_user_infos(user)
        )

    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def user_avatar(self, interaction: discord.Interaction, member: Member):
        """Get the avatar of a user"""
        return await interaction.response.send_message(
            embed=InformationHandler.get_user_avatar(member)
        )
