from random import random

from discord import Embed, SlashCommandGroup
from discord.ext import commands


class Misc(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.fancy_name = "Misc"

    # misc = SlashCommandGroup("misc", "Miscelanious commands!")

    @commands.command()
    async def help(self, ctx):
        embed = Embed(
            description="Get more information about these [commands](https://www.youtube.com/watch?v=dQw4w9WgXcQ)."
        )
        for name, cog in self.client.cogs.items():
            field = {"name": cog.fancy_name, "value": []}
            for cmd in cog.get_commands():
                field["value"].append(cmd.name)
            embed.add_field(
                name=field["name"], value=", ".join(field["value"]), inline=False
            )
        await ctx.send(embed=embed)
        return

    async def help_slash(self, ctx):
        await self.help(ctx)

    @commands.command()
    async def ping(self, ctx):
        bot_latency = round(self.client.latency * 1000)
        embed = Embed(description=":ping_pong: Pong !")
        msg = await ctx.channel.send(embed=embed)
        embed.add_field(name="Bot latency", value=f"{bot_latency} ms", inline=True)
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
        await msg.edit(embed=embed)
        return

    @commands.command(aliases=["flip"], name="flipcoin")
    async def flip_coin(self, ctx):
        result = "Heads" if round(random()) else "Tails"
        await ctx.channel.send(result)
        return
