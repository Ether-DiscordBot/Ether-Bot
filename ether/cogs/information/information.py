from typing import Optional
from discord import Embed, Member, SlashCommandGroup, user_command
from discord.ext import commands
from humanize import naturaldate, naturalsize


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
        self.fancy_name = "ℹ️ Information"
        self.help_icon = "ℹ️"
        self.client = client

    infos = SlashCommandGroup("infos", "Infos commands!")

    @infos.command(name="user")
    async def user(self, ctx, *, member: Member = None):
        member = member or ctx.author
        await ctx.respond(embed=InformationHandler.get_user_infos(member))

    @user_command(name="User infos")
    async def user_infos(self, ctx, *, member: Member):
        await ctx.respond(embed=InformationHandler.get_user_infos(member))

    @infos.command(name="server")
    async def server(self, ctx):
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
    async def avatar(self, ctx, member: Optional[Member] = None):
        user = member or ctx.author
        return await ctx.respond(embed=InformationHandler.get_user_avatar(user))

    @user_command(name="User avatar")
    async def user_avatar(self, ctx, member: Member):
        return await ctx.respond(embed=InformationHandler.get_user_avatar(member))
