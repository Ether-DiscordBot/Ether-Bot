import os
import requests

from discord import Embed, SlashCommandGroup
from discord.ext import commands

from ether.core.utils import EtherEmbeds


class Nasa(commands.Cog, name="nasa"):
    def __init__(self, client) -> None:
        self.fancy_name = "Nasa"
        self.client = client
        self.api_key = os.environ["NASA_API_KEY"]
    
    nasa = SlashCommandGroup("nasa", "Nasa commands!")
    
    @nasa.command(name="apod")
    async def apod(self, ctx):
        r = requests.get(f"https://api.nasa.gov/planetary/apod?api_key={self.api_key}&thumbs=true")
        
        if not r.ok:
            return ctx.respond(embed=EtherEmbeds.error("Sorry, an error has occurred."))
        
        res = r.json()
        
        image = None
        if res['media_type'] == "video":
            if res['thumbnail_url']:
                image = res['thumbnail_url']
        elif res['media_type'] == "image":
            image = res['hdurl']
        else:
            return ctx.respond(embed=EtherEmbeds.error("Sorry, unknow media type."))
        
        embed = Embed(
            title=res["title"],
            url=res['url']
            )
        embed.set_footer(text="Powered by Nasa")
        if image:
            embed.set_image(url=image)
        
        await ctx.respond(embed=embed)