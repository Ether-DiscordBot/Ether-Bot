from typing import Optional

from discord import Embed, Member, SlashCommandGroup, user_command
from discord.ext import commands
from humanize import naturaldate, naturalsize
from pycord18n.extension import _

from ether.core.i18n import locale_doc
from ether.core.constants import Emoji


class InformationHandler:
    def get_user_infos(self) -> Embed:
        avatar = self.display_avatar

        embed = Embed(description=f"**ID:** {self.id}")
        embed.set_author(
            name=f"{self.name}#{self.discriminator}", icon_url=avatar, url=avatar
        )

        embed.set_thumbnail(url=avatar)
        embed.add_field(
            name="Account creation date",
            value=naturaldate(self.created_at),
            inline=False,
        )

        embed.add_field(
            name="Server join date",
            value=naturaldate(self.joined_at),
            inline=False,
        )

        return embed

    def get_user_avatar(self, user) -> Embed:
        return Embed(
            description="**{0.display_name}'s** [avatar]({0.avatar_url}):".format(user)
        ).set_image(url=user.display_avatar)


class Information(commands.Cog, name="information"):
    def __init__(self, client):
        self.help_icon = Emoji.INFORMATION
        self.client = client

    infos = SlashCommandGroup("infos", "Infos commands!")

    @infos.command(name="user")
    @locale_doc
    async def user(self, ctx, *, member: Member = None):
        """Get informations about a user"""
        member = member or ctx.author
        await ctx.respond(embed=InformationHandler.get_user_infos(member))

    @user_command(name="User infos")
    @locale_doc
    async def user_infos(self, ctx, *, member: Member):
        """Get informations about a user"""
        await ctx.respond(embed=InformationHandler.get_user_infos(member))

    @infos.command(name="server")
    @locale_doc
    async def server(self, ctx):
        """Get informations about the server"""
        guild = ctx.guild

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
            name="Additional informations",
            value=f"\t**Emoji:** {len(guild.emojis)}/{guild.emoji_limit}\n"
            f"\t**Sticker:** {len(guild.stickers)}/{guild.sticker_limit}\n"
            f"\t**Filesize:** {naturalsize(guild.filesize_limit, binary=True)}",
            inline=False,
        )

        await ctx.respond(embed=embed)

    @infos.command(name="avatar")
    @locale_doc
    async def avatar(self, ctx, member: Optional[Member] = None):
        """Get the avatar of a user"""
        user = member or ctx.author
        return await ctx.respond(embed=InformationHandler.get_user_avatar(user))

    @user_command(name="User avatar")
    @locale_doc
    async def user_avatar(self, ctx, member: Member):
        """Get the avatar of a user"""
        return await ctx.respond(embed=InformationHandler.get_user_avatar(member))
