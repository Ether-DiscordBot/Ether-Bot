from mochibot.core import Colour
from discord import Embed, User
from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: User, *, reason=None):

        if not member:
            embed = Embed(
                colour=Colour.ERROR, description=f"unknown {member.display_name} !"
            )
            return await ctx.send(embed=embed)

        embed = Embed(
            colour=Colour.SUCCESS,
            description=f"**{member.display_name}** as been kicked !\n**Reason:** {reason}",
        )
        try:
            await ctx.guild.kick(member)
            await ctx.send(embed=embed)
        except:
            embed = Embed(
                colour=Colour.ERROR,
                description="Can't do that. Probably because I don't have the "
                "permissions for.",
            )
            return await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: User, *, reason=None):

        if not member:
            embed = Embed(
                colour=Colour.ERROR, description=f"unknown {member.display_name} !"
            )
            return await ctx.send(embed=embed)

        try:
            embed = Embed(
                colour=Colour.SUCCESS,
                description=f"**{member.display_name}** as been banned !\n**Reason:** {reason}",
            )
            await ctx.guild.ban(member)
            await ctx.send(embed=embed)
        except Exception as exception:
            embed = Embed(
                colour=Colour.ERROR,
                description="Can't do that. Probably because I don't have the "
                "permissions for.",
            )
            return await ctx.send(embed=embed)
