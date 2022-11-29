from typing import Optional

from discord import ApplicationContext, Embed, Member, SlashCommandGroup, user_command
from discord.ext import commands
from humanize import naturaldate, naturalsize
from ether.core.i18n import _

from ether.core.constants import Emoji


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


class Information(commands.Cog, name="information"):
    def __init__(self, client):
        self.help_icon = Emoji.INFORMATION
        self.client = client

    infos = SlashCommandGroup("infos", "Infos commands!")

    @infos.command(name="user")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def user(self, ctx: ApplicationContext, member: Member = None):
        """Get informations about a user"""
        member = member or ctx.author
        await ctx.respond(embed=InformationHandler.get_user_infos(member))

    @user_command(name="User infos")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def user_infos(self, ctx: ApplicationContext, member: Member):
        """Get informations about a user"""
        await ctx.respond(embed=InformationHandler.get_user_infos(member))

    @infos.command(name="server")
    @commands.cooldown(1, 5, commands.BucketType.user)
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
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def avatar(self, ctx: ApplicationContext, member: Optional[Member] = None):
        """Get the avatar of a user"""
        user = member or ctx.author
        return await ctx.respond(embed=InformationHandler.get_user_avatar(user))

    @user_command(name="User avatar")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def user_avatar(self, ctx: ApplicationContext, member: Member):
        """Get the avatar of a user"""
        return await ctx.respond(embed=InformationHandler.get_user_avatar(member))
