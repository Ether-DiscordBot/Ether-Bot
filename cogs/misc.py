from discord import Embed
from discord.ext import commands

from PIL import Image
import requests
from io import BytesIO

import os

class Misc(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def ping(self, ctx):
        bot_latency = round(self.client.latency * 1000)
        embed = Embed(description=':ping_pong: Pong !')
        msg = await ctx.channel.send(embed=embed)
        embed.add_field(name='Bot latency', value='{0} ms'.format(bot_latency), inline=True)
        embed.add_field(name='User latency', value='{0} ms'.format(
            round((msg.created_at.timestamp() - ctx.message.created_at.timestamp()) * 1000)), inline=True)
        return await msg.edit(embed=embed)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def avatar(self, ctx):
        user = ctx.message.mentions[0] if ctx.message.mentions else ctx.message.author
        embed = Embed(description="**{0.display_name}'s** [avatar]({0.avatar_url}):".format(user))\
            .set_image(url=user.avatar_url_as(format='png', size=256))
        return await ctx.channel.send(embed=embed)

def setup(client):
    client.add_cog(Misc(client))
