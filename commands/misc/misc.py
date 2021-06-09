from discord import Embed
from discord.ext import commands
from random import random


class Misc(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.help_embed = HelpEmbed(self.client.commands).embed

    @commands.command()
    async def help(self, ctx):
        await ctx.send(embed=self.help_embed)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def ping(self, ctx):
        bot_latency = round(self.client.latency * 1000)
        embed = Embed(description=":ping_pong: Pong !")
        msg = await ctx.channel.send(embed=embed)
        embed.add_field(
            name="Bot latency", value="{0} ms".format(bot_latency), inline=True
        )
        embed.add_field(
            name="User latency",
            value="{0} ms".format(
                round(
                    (msg.created_at.timestamp() - ctx.message.created_at.timestamp())
                    * 1000
                )
            ),
            inline=True,
        )
        return await msg.edit(embed=embed)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def avatar(self, ctx):
        user = ctx.message.mentions[0] if ctx.message.mentions else ctx.message.author
        embed = Embed(
            description="**{0.display_name}'s** [avatar]({0.avatar_url}):".format(user)
        ).set_image(url=user.avatar_url_as(format="png", size=256))
        return await ctx.channel.send(embed=embed)

    @commands.command(aliases=["flip"])
    async def flipcoin(self, ctx):
        result = "Heads" if round(random()) else "Tails"
        return await ctx.channel.send(result)


class HelpEmbed:
    def __init__(self, commands):
        self._msg = ""
        for cmd in commands:
            self._msg += cmd.name + "\n"

        self.embed = Embed(description=self._msg)
