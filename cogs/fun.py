from discord.ext import commands
from discord import Embed

from random import randint

class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.command(aliases=['match'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def ship(self, ctx):
        mentions = ctx.message.mentions
        first_user = mentions[0] if len(mentions) >= 1 else None
        second_user = mentions[1] if len(mentions) >= 2 else None

        match_percent = randint(0, 100)

        author = ctx.author

        if first_user is None:
            embed = Embed(description=f"<@{author.id}> x <@{self.client.user.id}> -> ❤️ {match_percent}%")
        elif second_user is None:
            embed = Embed(description=f"<@{author.id}> x <@{first_user.id}> -> ❤️ {match_percent}%")
        else:
            embed = Embed(description=f"<@{first_user.id}> x <@{second_user.id}> -> ❤️ {match_percent}%")

        return await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Fun(client))